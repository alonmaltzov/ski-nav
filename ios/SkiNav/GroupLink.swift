import Foundation

/// Shares this phone's position with the trip group, natively, so it keeps going with the phone locked
/// in a pocket (the web page can't). The page tells us the server, our member secret and whether sharing
/// is on (bridge command "group"); SkiDay hands us each GPS update while tracking.
/// Only while tracking, at most every 30 s, never after 6 pm, and nothing when sharing is off.
final class GroupLink {
    static let shared = GroupLink()

    private let defaults = UserDefaults.standard
    private let lock = NSLock()
    private var url: String
    private var key: String
    private var secret: String
    private var sharing: Bool
    private var lastPost = Date.distantPast
    private var inFlight = false

    private init() {
        url = defaults.string(forKey: "group.url") ?? ""
        key = defaults.string(forKey: "group.key") ?? ""
        secret = defaults.string(forKey: "group.secret") ?? ""
        sharing = defaults.object(forKey: "group.sharing") as? Bool ?? true
    }

    /// From the page: {cmd:'group', url, key, secret, sharing}. An empty secret means "not in a group".
    func configure(_ body: [String: Any]) {
        lock.lock(); defer { lock.unlock() }
        url = (body["url"] as? String) ?? ""
        key = (body["key"] as? String) ?? ""
        secret = (body["secret"] as? String) ?? ""
        sharing = (body["sharing"] as? Bool) ?? true
        defaults.set(url, forKey: "group.url"); defaults.set(key, forKey: "group.key")
        defaults.set(secret, forKey: "group.secret"); defaults.set(sharing, forKey: "group.sharing")
        print("[app] group:", secret.isEmpty ? "none" : (sharing ? "sharing location" : "in a group, not sharing"))
    }

    var isActive: Bool { lock.lock(); defer { lock.unlock() }; return !secret.isEmpty && sharing && !url.isEmpty }

    /// Called on SkiDay's queue after each batch of fixes.
    func maybePost(lat: Double, lon: Double, acc: Double, speedMps: Double, onLift: Bool, run: String?, km: Double) {
        lock.lock()
        let now = Date()
        guard !secret.isEmpty, sharing, !url.isEmpty, !inFlight, now.timeIntervalSince(lastPost) >= 30,
              Calendar.current.component(.hour, from: now) < 18,
              let endpoint = URL(string: url.trimmingCharacters(in: CharacterSet(charactersIn: "/")) + "/rest/v1/rpc/post_position")
        else { lock.unlock(); return }
        lastPost = now; inFlight = true
        let (k, s) = (key, secret)
        lock.unlock()

        var body: [String: Any] = ["p_secret": s, "p_lat": lat, "p_lon": lon, "p_acc": acc, "p_speed": speedMps,
                                   "p_on_lift": onLift, "p_km": (km * 100).rounded() / 100]
        if let r = run, !r.isEmpty { body["p_run"] = r }
        var req = URLRequest(url: endpoint, timeoutInterval: 15)
        req.httpMethod = "POST"
        req.setValue(k, forHTTPHeaderField: "apikey")
        req.setValue("Bearer " + k, forHTTPHeaderField: "Authorization")
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        URLSession.shared.dataTask(with: req) { [weak self] _, resp, err in
            guard let self else { return }
            self.lock.lock(); self.inFlight = false; self.lock.unlock()
            let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
            if err != nil || code >= 300 {
                print("[app] group position not sent:", err?.localizedDescription ?? "HTTP \(code)")
                // removed from the trip: stop trying until the page sets us up again
                if code == 400 || code == 403 { self.lock.lock(); self.lastPost = Date().addingTimeInterval(300); self.lock.unlock() }
            }
        }.resume()
    }
}
