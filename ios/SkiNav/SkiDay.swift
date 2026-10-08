import ActivityKit
import Foundation

/// The phone's native ski day: runs every GPS fix through the shared SkiEngine, so totals keep counting
/// while the phone is locked, and shows them on the lock screen / Dynamic Island as a Live Activity.
final class SkiDay {
    static let shared = SkiDay()
    let engine = SkiEngine()
    private let queue = DispatchQueue(label: "skinav.skiday")
    private var activity: Activity<SkiActivityAttributes>?
    private var step: SkiGlance.Step?
    private var stepIndex = 0
    private var lastPos: [Double]?
    private var dayTitle = "Ski day"
    private var lastPush = Date.distantPast
    private var lastLift = false

    func begin(base: SkiTotals?) {
        queue.async {
            if let b = base { self.engine.seed(b) }
            self.startActivity()
        }
    }

    func end() {
        queue.async {
            self.activity = nil
            SkiDay.endAll()
        }
    }

    /// Remove every Ski Nav lock-screen activity, including leftovers from an earlier run of the app.
    static func endAll() {
        Task {
            for a in Activity<SkiActivityAttributes>.activities { await a.end(nil, dismissalPolicy: .immediate) }
        }
    }

    func setContext(lifts: [[[Double]]]?, title: String?, flat: Bool? = nil) {
        queue.async {
            if let f = flat { self.engine.flat = f }
            if let l = lifts { self.engine.liftLines = l }
            if let t = title { self.dayTitle = t }
        }
    }

    func setStep(_ st: SkiGlance.Step, liftLine: [[Double]]?, index: Int) {
        queue.async {
            self.step = st
            self.stepIndex = index
            self.engine.plannedLift = liftLine
            self.push(force: true)
            self.toWatch(force: true)
        }
    }

    /// What every glance shows right now.
    var glance: SkiGlance {
        SkiGlance.make(speedMps: engine.speedMps, totals: engine.totals, onLift: engine.onLift, at: lastPos, step: step)
    }

    /// Live numbers for the watch (the same SkiGlance the lock screen shows) plus the step index.
    private func liveBody() -> [String: Any]? {
        guard let data = try? JSONEncoder().encode(glance) else { return nil }
        return ["glance": data, "idx": stepIndex, "tracking": LocationService.shared.isTracking]
    }
    private func toWatch(force: Bool) {
        guard let live = liveBody() else { return }
        DispatchQueue.main.async { WatchLink.shared.sendLive(live, force: force) }
    }
    /// For the watch asking "what's happening now?" (it pulls when pushes don't arrive).
    func liveForWatch() -> [String: Any]? { queue.sync { liveBody() } }

    func ingest(_ fixes: [GeoFix]) {
        queue.async {
            var good: GeoFix?
            for f in fixes {
                self.engine.ingest(f)
                if f.acc <= 30 { self.lastPos = [f.lat, f.lon] }
                if f.acc <= 100 { good = f }   // friends get rough positions too
            }
            if let f = good {
                // where I am, for friends in the trip group (only when sharing is on; GroupLink throttles)
                let run = self.engine.onLift ? nil : self.step.map { $0.label.replacingOccurrences(of: #"^(Ski|Take|Walk to) "#, with: "", options: .regularExpression) }
                GroupLink.shared.maybePost(lat: f.lat, lon: f.lon, acc: f.acc, speedMps: self.engine.speedMps, onLift: self.engine.onLift,
                                           run: run, km: self.engine.totals.distM / 1000)
            }
            let liftChanged = self.engine.onLift != self.lastLift
            self.push(force: liftChanged)
            self.toWatch(force: liftChanged)
            self.lastLift = self.engine.onLift
        }
    }

    // MARK: Live Activity

    private var state: SkiActivityAttributes.ContentState { glance }

    private func startActivity() {
        guard ActivityAuthorizationInfo().areActivitiesEnabled else { print("[app] live activities are off in Settings"); return }
        // only ever one: reuse a running one (e.g. after stop/start or an app restart) and close any extras
        let running = Activity<SkiActivityAttributes>.activities.filter { $0.activityState == .active }
        if let keep = activity ?? running.first {
            activity = keep
            for a in Activity<SkiActivityAttributes>.activities where a.id != keep.id { Task { await a.end(nil, dismissalPolicy: .immediate) } }
            push(force: true)
            print("[app] live activity reused")
            return
        }
        do {
            activity = try Activity.request(attributes: SkiActivityAttributes(dayTitle: dayTitle, startedAt: Date()),
                                            content: .init(state: state, staleDate: nil))
            print("[app] live activity started")
        } catch {
            print("[app] live activity failed:", error.localizedDescription)
        }
    }

    /// Update at most every 5 s (iOS throttles faster updates anyway), immediately for lift/step changes.
    private func push(force: Bool) {
        guard let a = activity else { return }
        let now = Date()
        guard force || now.timeIntervalSince(lastPush) >= 5 else { return }
        lastPush = now; lastLift = engine.onLift
        let s = state
        Task { await a.update(.init(state: s, staleDate: now.addingTimeInterval(120))) }
    }
}
