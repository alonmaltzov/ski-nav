import Foundation
import UserNotifications

/// Games that must work with the phone locked: STOPPP (3 a day, fired after 3 minutes on a lift)
/// and the passport check (first crossing into Switzerland before noon). The page works out the
/// times and whose round it is and sends them here ("games"); this only watches the fixes.
final class Games {
    static let shared = Games()
    private let lock = NSLock()
    private var stops: [(n: Int, at: Double, who: String)] = []
    private var stopOn = true, borderOn = true
    private var border: [[Double]] = []
    private var day = ""
    private var liftSince: Double?
    private let defaults = UserDefaults.standard

    func configure(_ body: [String: Any]) {
        lock.lock(); defer { lock.unlock() }
        if let on = body["on"] as? [String: Any] { stopOn = (on["stop"] as? Bool) ?? true; borderOn = (on["border"] as? Bool) ?? true }
        stops = ((body["stops"] as? [[String: Any]]) ?? []).compactMap { s in
            guard let n = s["n"] as? Int, let at = s["at"] as? Double else { return nil }
            return (n, at, (s["who"] as? String) ?? "Someone’s")
        }
        border = (body["border"] as? [[Double]]) ?? []
        day = (body["day"] as? String) ?? ""
    }

    private func fired(_ key: String) -> Bool { defaults.bool(forKey: "game-\(day)-\(key)") }
    private func mark(_ key: String) { defaults.set(true, forKey: "game-\(day)-\(key)") }

    func onFix(_ f: GeoFix, onLift: Bool) {
        lock.lock(); defer { lock.unlock() }
        guard !day.isEmpty, f.acc <= 30 else { return }
        let now = Date().timeIntervalSince1970 * 1000
        guard now - f.t < 120_000 else { return }          // catching up on old fixes: too late to call it
        let hour = Calendar.current.component(.hour, from: Date(timeIntervalSince1970: f.t / 1000))
        if onLift {
            if liftSince == nil { liftSince = f.t }
            if stopOn, hour < 16, let since = liftSince, f.t - since >= 180_000,
               let s = stops.first(where: { f.t >= $0.at && !fired("stop\($0.n)") }) {
                mark("stop\(s.n)")
                notify(id: "stop-\(s.n)", title: "STOPPP 🥃", body: "\(s.who) round: flask out at the top of this lift.", event: "stop:\(s.n)", sound: "stoppp.caf")
            }
        } else { liftSince = nil }
        if borderOn, hour < 12, !fired("swiss"), Games.swiss(f.lat, f.lon, border) {
            mark("swiss")
            notify(id: "swiss", title: "Welcome to Switzerland 🇨🇭", body: "Passport check: who crossed first? Open Ski-Paz to see.", event: nil, sound: "passport.caf")
        }
    }

    static func swiss(_ lat: Double, _ lon: Double, _ b: [[Double]]) -> Bool {
        guard b.count >= 2 else { return false }
        for i in 0..<(b.count - 1) where b[i].count == 2 && b[i + 1].count == 2 {
            let (a0, o0, a1, o1) = (b[i][0], b[i][1], b[i + 1][0], b[i + 1][1])
            if lat <= a1 { return lon > o0 + (o1 - o0) * max(0, (lat - a0) / (a1 - a0)) }
        }
        return lon > (b.last?.last ?? 180)
    }

    private func notify(id: String, title: String, body: String, event: String?, sound: String) {
        let c = UNMutableNotificationContent()
        c.title = title; c.body = body
        c.sound = Bundle.main.url(forResource: sound, withExtension: nil) != nil ? UNNotificationSound(named: UNNotificationSoundName(sound)) : .default
        if #available(iOS 15.0, *) { c.interruptionLevel = .timeSensitive }
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: "game-\(id)", content: c, trigger: nil))
        print("[games]", title, body)
        if let e = event { DispatchQueue.main.async { if WebBridge.shared.pageReady { WebBridge.shared.send(event: e) } } }
    }
}
