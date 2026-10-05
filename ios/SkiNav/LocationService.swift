import Foundation
import CoreLocation

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
        manager.stopUpdatingLocation()
        manager.allowsBackgroundLocationUpdates = false
    }

    private func begin() {
        manager.allowsBackgroundLocationUpdates = true
        manager.showsBackgroundLocationIndicator = true
        manager.startUpdatingLocation()
    }

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
        let fixes = locations.filter { $0.horizontalAccuracy >= 0 }.map(Fix.init)
        guard !fixes.isEmpty else { return }
        queue.sync { pending.append(contentsOf: fixes) }
        save(fixes)
        DispatchQueue.main.async { WebBridge.shared.flushIfActive() }
    }

    func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        // transient errors (no signal in a tunnel or a gondola) are normal; keep going
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
