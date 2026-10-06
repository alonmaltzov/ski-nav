import Foundation
import WatchConnectivity

/// Phone -> watch: today's plan (kept until delivered) and, while tracking, live stats + current step.
final class WatchLink: NSObject, WCSessionDelegate {
    static let shared = WatchLink()
    private var pendingPlan: Data?
    private var lastLive = Date.distantPast

    func activate() {
        guard WCSession.isSupported() else { return }
        WCSession.default.delegate = self
        WCSession.default.activate()
    }

    private var ready: Bool {
        let s = WCSession.default
        return WCSession.isSupported() && s.activationState == .activated && s.isPaired && s.isWatchAppInstalled
    }

    /// Remember the latest plan and deliver it as soon as the watch link is up (it often isn't yet at app launch).
    func sendPlan(_ body: [String: Any]) {
        var ctx = body
        ctx.removeValue(forKey: "cmd")
        guard let data = try? JSONSerialization.data(withJSONObject: ctx) else { return }
        pendingPlan = data
        flushPlan()
    }

    private func flushPlan() {
        guard let data = pendingPlan, ready else {
            if pendingPlan != nil { print("[app] watch not ready yet, plan queued") }
            return
        }
        do {
            // applicationContext keeps only the latest plan and arrives even if the watch app is closed
            try WCSession.default.updateApplicationContext(["plan": data])
            print("[app] plan sent to watch")
        } catch {
            print("[app] plan to watch failed:", error.localizedDescription)
        }
    }

    /// Live numbers for the watch face while the phone tracks (only when the watch app is open and reachable).
    func sendLive(_ live: [String: Any], force: Bool) {
        guard ready, WCSession.default.isReachable else { return }
        let now = Date()
        guard force || now.timeIntervalSince(lastLive) >= 3 else { return }
        lastLive = now
        WCSession.default.sendMessage(["live": live], replyHandler: nil, errorHandler: nil)
    }

    func session(_ session: WCSession, activationDidCompleteWith state: WCSessionActivationState, error: Error?) {
        print("[app] watch link:", state == .activated ? "on" : "off", "paired:", session.isPaired, "installed:", session.isWatchAppInstalled)
        DispatchQueue.main.async { self.flushPlan() }
    }
    func sessionWatchStateDidChange(_ session: WCSession) { DispatchQueue.main.async { self.flushPlan() } }
    func sessionReachabilityDidChange(_ session: WCSession) { DispatchQueue.main.async { self.flushPlan() } }
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) { WCSession.default.activate() }
}
