import Foundation
import HealthKit
import CoreLocation
import WatchConnectivity
import WatchKit

/// One step of today's plan, as sent by the phone.
struct PlanStep: Codable, Identifiable {
    var id: Int { idx }
    var idx: Int = 0
    let l: String        // label, e.g. "Take Prolays chair"
    let t: String        // "run" | "lift" | "end"
    let c: String        // colour: blue, red, black, green, lift, end
    let len: Double
    let s: [Double]      // start [lat, lon]
    let e: [Double]      // end [lat, lon]
    let at: String
    // idx is set on the watch after decoding, the phone doesn't send it
    enum CodingKeys: String, CodingKey { case l, t, c, len, s, e, at }
}

/// What the phone is tracking right now (sent every few seconds while the watch app is open).
struct PhoneLive {
    var speedKmh: Double, km: Double, maxKmh: Double, vertM: Double
    var onLift: Bool, step: String, color: String, next: String, idx: Int, tracking: Bool
    var at: Date
}

struct Plan: Codable {
    let day: Int
    let title: String
    var steps: [PlanStep]
}

/// The ski day on the wrist: a Downhill Skiing workout (keeps GPS on with the screen off),
/// live speed / distance / max / vertical, lift detection, and the next step of the plan.
@MainActor
final class SkiSession: NSObject, ObservableObject {
    // live numbers
    @Published var running = false
    @Published var speedKmh: Double = 0
    @Published var maxKmh: Double = 0
    @Published var distanceKm: Double = 0
    @Published var verticalM: Double = 0
    @Published var onLift = false
    @Published var gpsOK = false
    @Published var elapsed: TimeInterval = 0
    @Published var message: String?

    // plan
    @Published var plan: Plan?
    @Published var current = 0
    @Published var phone: PhoneLive?

    private let health = HKHealthStore()
    private var session: HKWorkoutSession?
    private var builder: HKLiveWorkoutBuilder?
    private let location = CLLocationManager()
    private let engine = SkiEngine()
    private var startDate: Date?
    private var timer: Timer?

    override init() {
        super.init()
        location.delegate = self
        location.desiredAccuracy = kCLLocationAccuracyBest
        location.activityType = .fitness
        if WCSession.isSupported() {
            WCSession.default.delegate = self
            WCSession.default.activate()
        }
        if let data = UserDefaults.standard.data(forKey: "plan"), let p = try? JSONDecoder().decode(Plan.self, from: data) {
            plan = p
        }
        current = UserDefaults.standard.integer(forKey: "current")
    }

    var step: PlanStep? {
        guard let p = plan, current < p.steps.count else { return nil }
        return p.steps[current]
    }
    var nextLift: PlanStep? {
        guard let p = plan, current + 1 < p.steps.count else { return nil }
        return p.steps[(current + 1)...].first { $0.t == "lift" }
    }
    var nextStep: PlanStep? {
        guard let p = plan, current + 1 < p.steps.count else { return nil }
        return p.steps[current + 1]
    }

    // MARK: start / stop

    func start() {
        let share: Set<HKSampleType> = [HKObjectType.workoutType(),
                                         HKQuantityType(.distanceDownhillSnowSports),
                                         HKQuantityType(.activeEnergyBurned)]
        let read: Set<HKObjectType> = [HKObjectType.workoutType(), HKQuantityType(.heartRate),
                                       HKQuantityType(.distanceDownhillSnowSports)]
        health.requestAuthorization(toShare: share, read: read) { [weak self] ok, _ in
            Task { @MainActor in
                guard let self else { return }
                self.location.requestWhenInUseAuthorization()
                self.beginWorkout(healthOK: ok)
            }
        }
    }

    private func beginWorkout(healthOK: Bool) {
        let cfg = HKWorkoutConfiguration()
        cfg.activityType = .downhillSkiing
        cfg.locationType = .outdoor
        do {
            let s = try HKWorkoutSession(healthStore: health, configuration: cfg)
            let b = s.associatedWorkoutBuilder()
            b.dataSource = HKLiveWorkoutDataSource(healthStore: health, workoutConfiguration: cfg)
            session = s; builder = b
            let now = Date()
            s.startActivity(with: now)
            b.beginCollection(withStart: now) { _, _ in }
        } catch {
            // without HealthKit the watch still tracks, but only while the screen is on
            message = "Workout not allowed: tracking only while the screen is on."
        }
        startDate = Date()
        running = true
        location.startUpdatingLocation()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            Task { @MainActor in
                guard let self, let s = self.startDate else { return }
                self.elapsed = Date().timeIntervalSince(s)
            }
        }
    }

    func stop() {
        running = false
        location.stopUpdatingLocation()
        timer?.invalidate(); timer = nil
        session?.end()
        let b = builder
        b?.endCollection(withEnd: Date()) { _, _ in
            b?.finishWorkout { _, _ in }
        }
        builder = nil
        session = nil
    }

    func nextManually() { advance() }
    func previousManually() { if current > 0 { current -= 1; engine.resetStep(); saveCurrent() } }

    private func advance() {
        guard let p = plan, current < p.steps.count - 1 else { return }
        current += 1
        engine.resetStep()
        saveCurrent()
        WKInterfaceDevice.current().play(.directionUp)
    }

    private func saveCurrent() { UserDefaults.standard.set(current, forKey: "current") }

    // MARK: per-fix logic (same rules as the phone app)

    fileprivate func handle(_ loc: CLLocation) {
        guard loc.horizontalAccuracy >= 0 else { return }
        gpsOK = loc.horizontalAccuracy <= 30
        // same rules as the phone: the shared SkiEngine (no lift map on the watch, so lifts are found by climb rate)
        if let s = step, s.t == "lift", s.s.count == 2, s.e.count == 2 { engine.plannedLift = [s.s, s.e] } else { engine.plannedLift = nil }
        engine.ingest(GeoFix(lat: loc.coordinate.latitude, lon: loc.coordinate.longitude, acc: loc.horizontalAccuracy,
                             alt: loc.verticalAccuracy >= 0 ? loc.altitude : nil, speed: loc.speed >= 0 ? loc.speed : nil,
                             t: loc.timestamp.timeIntervalSince1970 * 1000))
        let tot = engine.totals
        speedKmh = engine.speedMps * 3.6
        distanceKm = tot.distM / 1000
        maxKmh = tot.maxMps * 3.6
        verticalM = tot.vertM
        onLift = engine.onLift

        // next step: reached the end of this one (loops need most of their length done first)
        if let s = step, s.t != "end" {
            let isLoop = distance(between: s.s, s.e) < 80
            if distance(to: s.e, from: loc) < max(35, loc.horizontalAccuracy) && (!isLoop || engine.stepDistM > 0.6 * s.len) {
                advance()
            }
        }
    }

    private func distance(to p: [Double], from loc: CLLocation) -> Double {
        guard p.count == 2 else { return .infinity }
        return CLLocation(latitude: p[0], longitude: p[1]).distance(from: loc)
    }
    private func distance(between a: [Double], _ b: [Double]) -> Double {
        guard a.count == 2, b.count == 2 else { return .infinity }
        return CLLocation(latitude: a[0], longitude: a[1]).distance(from: CLLocation(latitude: b[0], longitude: b[1]))
    }

    /// Pull the plan from the phone (when reachable) instead of only waiting for a push.
    func askForPlan() {
        let s = WCSession.default
        guard s.activationState == .activated, s.isReachable else { return }
        s.sendMessage(["want": "plan"], replyHandler: { reply in
            if let data = reply["plan"] as? Data { Task { @MainActor in self.receive(planData: data) } }
        }, errorHandler: { e in print("[watch] ask for plan failed:", e.localizedDescription) })
    }

    fileprivate func receive(live d: [String: Any]) {
        let l = PhoneLive(speedKmh: d["speed"] as? Double ?? 0, km: d["km"] as? Double ?? 0, maxKmh: d["max"] as? Double ?? 0,
                          vertM: d["vert"] as? Double ?? 0, onLift: d["lift"] as? Bool ?? false, step: d["step"] as? String ?? "",
                          color: d["color"] as? String ?? "lift", next: d["next"] as? String ?? "", idx: d["idx"] as? Int ?? 0,
                          tracking: d["tracking"] as? Bool ?? false, at: Date())
        if phone?.idx != l.idx, let p = plan, l.idx < p.steps.count, l.idx != current {
            current = l.idx; engine.resetStep(); saveCurrent()   // follow the phone's step
        }
        if phone == nil { print("[watch] live data from phone: \(l.step)") }
        phone = l
    }

    fileprivate func receive(planData: Data) {
        guard var p = try? JSONDecoder().decode(Plan.self, from: planData) else {
            print("[watch] plan received but could not be read (\(planData.count) bytes)"); message = "Plan from phone could not be read"; return
        }
        print("[watch] plan received: \(p.title), \(p.steps.count) steps")
        for i in p.steps.indices { p.steps[i].idx = i }
        let newDay = plan?.day != p.day
        plan = p
        UserDefaults.standard.set(try? JSONEncoder().encode(p), forKey: "plan")
        if newDay { current = 0; engine.resetStep(); saveCurrent() }
    }
}

extension SkiSession: CLLocationManagerDelegate {
    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        Task { @MainActor in for l in locations { self.handle(l) } }
    }
    nonisolated func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {}
}

extension SkiSession: WCSessionDelegate {
    nonisolated func session(_ session: WCSession, activationDidCompleteWith state: WCSessionActivationState, error: Error?) {
        print("[watch] link to phone:", state == .activated ? "on" : "off", "reachable:", session.isReachable)
        Task { @MainActor in self.askForPlan() }
        let ctx = session.receivedApplicationContext
        if let data = ctx["plan"] as? Data { Task { @MainActor in self.receive(planData: data) } }
    }
    nonisolated func session(_ session: WCSession, didReceiveApplicationContext ctx: [String: Any]) {
        if let data = ctx["plan"] as? Data { Task { @MainActor in self.receive(planData: data) } }
    }
    nonisolated func sessionReachabilityDidChange(_ session: WCSession) {
        if session.isReachable { Task { @MainActor in self.askForPlan() } }
    }
    nonisolated func session(_ session: WCSession, didReceiveMessage msg: [String: Any]) {
        if let live = msg["live"] as? [String: Any] {
            let copy = live as NSDictionary
            Task { @MainActor in self.receive(live: copy as! [String: Any]) }
        }
    }
}
