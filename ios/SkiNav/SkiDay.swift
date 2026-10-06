import ActivityKit
import Foundation

/// The phone's native ski day: runs every GPS fix through the shared SkiEngine, so totals keep counting
/// while the phone is locked, and shows them on the lock screen / Dynamic Island as a Live Activity.
final class SkiDay {
    static let shared = SkiDay()
    let engine = SkiEngine()
    private let queue = DispatchQueue(label: "skinav.skiday")
    private var activity: Activity<SkiActivityAttributes>?
    private var step = ("", "lift")
    private var nextLift = ""
    private var stepIndex = 0
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

    func setContext(lifts: [[[Double]]]?, title: String?) {
        queue.async {
            if let l = lifts { self.engine.liftLines = l }
            if let t = title { self.dayTitle = t }
        }
    }

    func setStep(label: String, color: String, liftLine: [[Double]]?, nextLift: String, index: Int) {
        queue.async {
            self.step = (label, color)
            self.nextLift = nextLift
            self.stepIndex = index
            self.engine.plannedLift = liftLine
            self.push(force: true)
            self.toWatch(force: true)
        }
    }

    /// Live numbers for the watch: speed, totals, what you're on now and the next lift.
    private func toWatch(force: Bool) {
        let t = engine.totals
        let live: [String: Any] = ["speed": engine.speedMps * 3.6, "km": t.distM / 1000, "max": t.maxMps * 3.6, "vert": t.vertM,
                                   "lift": engine.onLift, "step": step.0, "color": step.1, "next": nextLift, "idx": stepIndex,
                                   "tracking": LocationService.shared.isTracking]
        DispatchQueue.main.async { WatchLink.shared.sendLive(live, force: force) }
    }

    func ingest(_ fixes: [GeoFix]) {
        queue.async {
            for f in fixes { self.engine.ingest(f) }
            let liftChanged = self.engine.onLift != self.lastLift
            self.push(force: liftChanged)
            self.toWatch(force: liftChanged)
            self.lastLift = self.engine.onLift
        }
    }

    // MARK: Live Activity

    private var state: SkiActivityAttributes.ContentState {
        let t = engine.totals
        return .init(speedKmh: Int((engine.speedMps * 3.6).rounded()), km: t.distM / 1000, maxKmh: Int((t.maxMps * 3.6).rounded()),
                     vertM: Int(t.vertM.rounded()), onLift: engine.onLift, step: step.0, stepColor: step.1)
    }

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
