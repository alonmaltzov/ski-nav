import Foundation

/// Small text helpers shared by the phone, the lock screen, the Dynamic Island and the watch,
/// so every glance names things the same way.
enum SkiText {
    /// "Ski Chaux Fleuries (red) → Grand Plan" -> "Chaux Fleuries", "Take Ardent gondola" -> "Ardent gondola".
    static func short(_ label: String) -> String {
        var s = label
        if let r = s.range(of: "→") { s = String(s[..<r.lowerBound]) }
        if let r = s.range(of: "->") { s = String(s[..<r.lowerBound]) }
        s = s.trimmingCharacters(in: .whitespaces)
        for p in ["Ski ", "Take ", "Traverse to ", "Walk to ", "Ride "] where s.hasPrefix(p) {
            s = String(s.dropFirst(p.count)); break
        }
        if let open = s.lastIndex(of: "("), s.hasSuffix(")") {
            let inside = s[s.index(after: open)..<s.index(before: s.endIndex)].lowercased()
            if ["blue", "red", "black", "green", "orange", "lift", "link"].contains(inside) {
                s = String(s[..<open])
            }
        }
        return s.trimmingCharacters(in: .whitespaces)
    }

    /// "red" -> "Red", "lift" -> "Lift".
    static func colorWord(_ c: String) -> String {
        switch c {
        case "blue", "red", "black", "green", "orange": return c.prefix(1).uppercased() + c.dropFirst()
        case "end": return "Last run"
        default: return "Lift"
        }
    }

    /// Great-circle metres between [lat, lon] points.
    static func hav(_ a: [Double], _ b: [Double]) -> Double {
        guard a.count >= 2, b.count >= 2 else { return .infinity }
        let r = 6_371_000.0, d = Double.pi / 180
        let dLat = (b[0] - a[0]) * d, dLon = (b[1] - a[1]) * d
        let h = sin(dLat / 2) * sin(dLat / 2) + cos(a[0] * d) * cos(b[0] * d) * sin(dLon / 2) * sin(dLon / 2)
        return 2 * r * asin(min(1, sqrt(h)))
    }

    /// How far up a lift you are (0...1) and roughly how many minutes to the top (lifts run ~5 m/s).
    static func liftProgress(at p: [Double], start: [Double], end: [Double]) -> (Double, Int) {
        let total = hav(start, end)
        guard total.isFinite, total > 20 else { return (0, 0) }
        let left = hav(p, end)
        let done = max(0, min(1, 1 - left / total))
        return (done, max(1, Int((min(left, total) / 5 / 60).rounded(.up))))
    }

    /// "12.4 km", or "850 m" under 1 km.
    static func km(_ metres: Double) -> String {
        metres < 1000 ? "\(Int((metres / 10).rounded() * 10)) m" : String(format: "%.1f km", metres / 1000)
    }
}
