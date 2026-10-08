import Foundation
import CoreLocation
import UIKit

/// One GPS reading, in the shape the web app's onFix() expects.
struct Fix: Codable {
    let lat: Double
    let lon: Double
    let acc: Double
    let alt: Double?
    let speed: Double?
    let heading: Double?
    let t: Double   // milliseconds since 1970

    init(_ l: CLLocation) {
        lat = l.coordinate.latitude
        lon = l.coordinate.longitude
        acc = l.horizontalAccuracy
        alt = l.verticalAccuracy >= 0 ? l.altitude : nil
        speed = l.speed >= 0 ? l.speed : nil
        heading = l.course >= 0 ? l.course : nil
        t = l.timestamp.timeIntervalSince1970 * 1000
    }
}

/// Native GPS that keeps running with the screen locked.
/// Fixes are buffered (and saved to disk) until the web app is in the foreground to receive them.
final class LocationService: NSObject, ObservableObject, CLLocationManagerDelegate {
    static let shared = LocationService()

    private let manager = CLLocationManager()
    private var pending: [Fix] = []
    private let queue = DispatchQueue(label: "skinav.location")
    @Published private(set) var isTracking = false
    private var logCount = 0

    private var trackURL: URL {
        let day = ISO8601DateFormatter.string(from: Date(), timeZone: .current, formatOptions: [.withFullDate])
        return FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("track-\(day).jsonl")
    }

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 2
        manager.activityType = .fitness
        manager.pausesLocationUpdatesAutomatically = false
    }

    func start() {
        isTracking = true
        switch manager.authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse:
            // ask for "Always" so tracking survives the lock screen; iOS shows this prompt once
            manager.requestAlwaysAuthorization()
            begin()
        case .authorizedAlways:
            begin()
        default:
            WebBridge.shared.send(event: "denied")
        }
    }

    func stop() {
        isTracking = false
        SkiDay.shared.end()
        updates?.cancel(); updates = nil
        background?.invalidate(); background = nil
        probe?.invalidate(); probe = nil
    }

    private var updates: Task<Void, Never>?
    private var background: CLBackgroundActivitySession?

    /// iOS 17 live updates: about one fix per second, kept alive with the phone locked by a background session.
    private func begin() {
        guard updates == nil else { return }
        print("[app] location updates on, auth=\(manager.authorizationStatus.rawValue)")
        background = CLBackgroundActivitySession()
        updates = Task { [weak self] in
            do {
                for try await u in CLLocationUpdate.liveUpdates(.fitness) {
                    if Task.isCancelled { break }
                    guard let self, let l = u.location else { continue }
                    self.received([l])
                }
            } catch {
                print("[app] location updates stopped:", error.localizedDescription)
            }
        }
        if ProcessInfo.processInfo.arguments.contains("-qaTour"), probe == nil {
            // QA only: what CoreLocation holds right now, independent of delegate callbacks
            probe = Timer.scheduledTimer(withTimeInterval: 3, repeats: true) { [weak self] _ in
                guard let self, let l = self.manager.location else { return }
                print("[app] probe \(String(format: "%.5f,%.5f", l.coordinate.latitude, l.coordinate.longitude)) age=\(Int(-l.timestamp.timeIntervalSinceNow))s callbacks=\(self.logCount) state=\(UIApplication.shared.applicationState.rawValue)")
            }
        }
    }
    private var probe: Timer?

    /// Hand over everything collected since the last call.
    func drain() -> [Fix] {
        queue.sync {
            let out = pending
            pending.removeAll()
            return out
        }
    }

    // MARK: CLLocationManagerDelegate

    func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        if wantLocate, [.authorizedWhenInUse, .authorizedAlways].contains(m.authorizationStatus) { m.requestLocation() }
        guard isTracking else { return }
        switch m.authorizationStatus {
        case .authorizedWhenInUse:
            m.requestAlwaysAuthorization()
            begin()
        case .authorizedAlways:
            begin()
        case .denied, .restricted:
            WebBridge.shared.send(event: "denied")
        default:
            break
        }
    }

    func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        // one-off "where am I" for the ME button (tracking itself comes from live updates)
        if wantLocate, let l = locations.last { wantLocate = false; sendLocated(l) }
    }

    // MARK: ME button and compass

    private var wantLocate = false
    private var wantHeading = false
    private var lastHeadingSent = Date.distantPast

    func locate() {
        wantLocate = true
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .denied, .restricted: wantLocate = false; WebBridge.shared.send(event: "denied")
        default:
            if let l = manager.location, -l.timestamp.timeIntervalSinceNow < 20 { sendLocated(l) }
            manager.requestLocation()
        }
    }

    func compass(_ on: Bool) {
        wantHeading = on
        if on {
            guard CLLocationManager.headingAvailable() else { WebBridge.shared.send(event: "nocompass"); return }
            manager.headingFilter = 2
            manager.startUpdatingHeading()
        } else {
            manager.stopUpdatingHeading()
        }
    }

    func locationManager(_ m: CLLocationManager, didUpdateHeading h: CLHeading) {
        guard wantHeading, h.headingAccuracy >= 0 else { return }
        let now = Date()
        guard now.timeIntervalSince(lastHeadingSent) > 0.1 else { return }
        lastHeadingSent = now
        let deg = h.trueHeading >= 0 ? h.trueHeading : h.magneticHeading
        WebBridge.shared.js("window.__native && window.__native.heading && window.__native.heading(\(deg))")
    }

    private func sendLocated(_ l: CLLocation) {
        let f = Fix(l)
        guard let d = try? JSONEncoder().encode(f), let s = String(data: d, encoding: .utf8) else { return }
        WebBridge.shared.js("window.__native && window.__native.located && window.__native.located(\(s))")
    }

    private func received(_ locations: [CLLocation]) {
        let fixes = locations.filter { $0.horizontalAccuracy >= 0 }.map(Fix.init)
        logCount += locations.count
        if logCount <= 40, let l = locations.last {
            print("[app] gps #\(logCount) \(String(format: "%.5f,%.5f", l.coordinate.latitude, l.coordinate.longitude)) acc=\(Int(l.horizontalAccuracy)) speed=\(String(format: "%.1f", l.speed)) batch=\(locations.count)")
        }
        guard !fixes.isEmpty else { return }
        // native totals: keep counting while the page is asleep (phone locked) and feed the lock screen
        SkiDay.shared.ingest(fixes.map { GeoFix(lat: $0.lat, lon: $0.lon, acc: $0.acc, alt: $0.alt, speed: $0.speed, t: $0.t) })
        queue.sync { pending.append(contentsOf: fixes) }
        save(fixes)
        DispatchQueue.main.async { WebBridge.shared.flushIfActive() }
    }

    func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        if wantLocate { print("[app] locate failed:", error.localizedDescription) }
        // transient errors (no signal in a tunnel or a gondola) are normal; keep going
    }

    /// Delete every saved day log (track-YYYY-MM-DD.jsonl). Not while tracking.
    func clearSaved() {
        guard !isTracking else { return }
        let dir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let files = (try? FileManager.default.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)) ?? []
        var n = 0
        for f in files where f.lastPathComponent.hasPrefix("track-") && f.pathExtension == "jsonl" {
            if (try? FileManager.default.removeItem(at: f)) != nil { n += 1 }
        }
        queue.sync { pending.removeAll() }
        print("[app] cleared \(n) saved track files")
    }

    private func save(_ fixes: [Fix]) {
        let enc = JSONEncoder()
        var data = Data()
        for f in fixes {
            if let d = try? enc.encode(f) { data.append(d); data.append(0x0A) }
        }
        let url = trackURL
        if let h = try? FileHandle(forWritingTo: url) {
            h.seekToEndOfFile(); h.write(data); try? h.close()
        } else {
            try? data.write(to: url)
        }
    }
}
