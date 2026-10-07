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
    init(l: String, t: String, c: String, len: Double, s: [Double], e: [Double], at: String) {
        self.l = l; self.t = t; self.c = c; self.len = len; self.s = s; self.e = e; self.at = at
    }
    // idx is set on the watch after decoding, the phone doesn't send it
    enum CodingKeys: String, CodingKey { case l, t, c, len, s, e, at }
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
    /// What the iPhone is tracking right now (sent every few seconds while this app is open), and when it arrived.
    @Published var phoneGlance: SkiGlance?
    @Published var phoneAt = Date.distantPast
    @Published var phoneTracking = false
    private var phoneIdx = -1
    /// The watch's own numbers while it runs its own workout.
    @Published var ownGlance = SkiGlance()
    private var lastPos: [Double]?

    /// QA screenshots: `-demo now|lift|steps` fills the screens with a sample day.
    static let demoScreen: String? = {
        let a = ProcessInfo.processInfo.arguments
        guard let i = a.firstIndex(of: "-demo"), i + 1 < a.count else { return nil }
        return a[i + 1]
    }()

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
        if let d = SkiSession.demoScreen { loadDemo(d) }
    }

    /// What the glances show: the watch's own tracking when it runs, else the phone's (if recent).
    var glance: SkiGlance? {
        if running { return ownGlance }
        if let g = phoneGlance, Date().timeIntervalSince(phoneAt) < 20 { return g }
        return nil
    }
    /// True when the numbers on screen come from the iPhone.
    var fromPhone: Bool { !running && glance != nil }

    /// The current plan step in the shape glances use.
    func glanceStep() -> SkiGlance.Step? {
        guard let s = step else { return nil }
        let nl = nextLift, th = nextStep
        return SkiGlance.Step(label: s.l, color: s.c, ends: [s.s, s.e], nextLift: nl?.l ?? "", nextLiftAt: nl?.s,
                              then: th?.l ?? "", thenColor: th?.c ?? "lift")
    }

    private func loadDemo(_ screen: String) {
        let steps: [PlanStep] = [
            .init(l: "Take Chaux Fleurie chair", t: "lift", c: "lift", len: 1064, s: [46.20701, 6.77827], e: [46.21169, 6.79035], at: "9:45"),
            .init(l: "Ski Chaux Fleuries (red) → Grand Plan (blue)", t: "run", c: "red", len: 4458, s: [46.21169, 6.79035], e: [46.21378, 6.76099], at: "9:54"),
            .init(l: "Take Ardent gondola", t: "lift", c: "lift", len: 1470, s: [46.21378, 6.76099], e: [46.20792, 6.77813], at: "10:19"),
            .init(l: "Ski Parchets (blue)", t: "run", c: "blue", len: 1762, s: [46.20792, 6.77813], e: [46.21378, 6.76099], at: "10:28"),
            .init(l: "Take Ardent gondola", t: "lift", c: "lift", len: 1470, s: [46.21378, 6.76099], e: [46.20792, 6.77813], at: "10:37"),
            .init(l: "Ski Les Tannes (red)", t: "run", c: "red", len: 2055, s: [46.20792, 6.77813], e: [46.20701, 6.77827], at: "10:46"),
        ]
        var p = Plan(day: 1, title: "Avoriaz north + Lindarets", steps: steps)
        for i in p.steps.indices { p.steps[i].idx = i }
        plan = p
        let onLift = screen == "lift"
        current = onLift ? 2 : 1
        let pos = onLift ? [46.2100, 6.7710] : [46.2125, 6.7800]
        var tot = SkiTotals(); tot.distM = 12_400; tot.maxMps = 54 / 3.6; tot.vertM = 1840
        phoneGlance = SkiGlance.make(speedMps: onLift ? 5 / 3.6 : 42 / 3.6, totals: tot, onLift: onLift, at: pos, step: glanceStep())
        phoneAt = .distantFuture
        phoneTracking = true
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
        lastPos = [loc.coordinate.latitude, loc.coordinate.longitude]
        ownGlance = SkiGlance.make(speedMps: engine.speedMps, totals: tot, onLift: engine.onLift, at: lastPos, step: glanceStep())

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
        if SkiSession.demoScreen != nil { return }
        guard let data = d["glance"] as? Data, let g = try? JSONDecoder().decode(SkiGlance.self, from: data) else { return }
        let idx = d["idx"] as? Int ?? 0
        if idx != phoneIdx, let p = plan, idx < p.steps.count, idx != current {
            current = idx; engine.resetStep(); saveCurrent()   // follow the phone's step
        }
        phoneIdx = idx
        if phoneGlance == nil { print("[watch] live data from phone: \(g.run) \(g.speedKmh) km/h") }
        phoneGlance = g
        phoneAt = Date()
        phoneTracking = d["tracking"] as? Bool ?? false
    }

    fileprivate func receive(planData: Data) {
        if SkiSession.demoScreen != nil { return }   // QA screenshots keep the sample day
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
