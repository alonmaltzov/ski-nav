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
            let a = self.activity; self.activity = nil
            Task { await a?.end(nil, dismissalPolicy: .immediate) }
        }
    }

    func setContext(lifts: [[[Double]]]?, title: String?) {
        queue.async {
            if let l = lifts { self.engine.liftLines = l }
            if let t = title { self.dayTitle = t }
        }
    }

    func setStep(label: String, color: String, liftLine: [[Double]]?) {
        queue.async {
            self.step = (label, color)
            self.engine.plannedLift = liftLine
            self.push(force: true)
        }
    }

    func ingest(_ fixes: [GeoFix]) {
        queue.async {
            for f in fixes { self.engine.ingest(f) }
            self.push(force: self.engine.onLift != self.lastLift)
        }
    }

    // MARK: Live Activity

    private var state: SkiActivityAttributes.ContentState {
        let t = engine.totals
        return .init(speedKmh: Int((engine.speedMps * 3.6).rounded()), km: t.distM / 1000, maxKmh: Int((t.maxMps * 3.6).rounded()),
                     vertM: Int(t.vertM.rounded()), onLift: engine.onLift, step: step.0, stepColor: step.1)
    }

    private func startActivity() {
        guard activity == nil, ActivityAuthorizationInfo().areActivitiesEnabled else {
            print("[app] live activity not started (disabled or already running)"); return
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
