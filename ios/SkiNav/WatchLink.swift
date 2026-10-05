import Foundation
import WatchConnectivity

/// Sends today's plan from the phone to the watch.
final class WatchLink: NSObject, WCSessionDelegate {
    static let shared = WatchLink()

    func activate() {
        guard WCSession.isSupported() else { return }
        WCSession.default.delegate = self
        WCSession.default.activate()
    }

    func sendPlan(_ body: [String: Any]) {
        guard WCSession.isSupported(), WCSession.default.activationState == .activated,
              WCSession.default.isPaired, WCSession.default.isWatchAppInstalled else { return }
        // applicationContext keeps only the latest plan and is delivered even if the watch app is closed
        var ctx = body
        ctx.removeValue(forKey: "cmd")
        if let data = try? JSONSerialization.data(withJSONObject: ctx) {
            try? WCSession.default.updateApplicationContext(["plan": data])
        }
    }

    func session(_ session: WCSession, activationDidCompleteWith state: WCSessionActivationState, error: Error?) {}
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) { WCSession.default.activate() }
}
