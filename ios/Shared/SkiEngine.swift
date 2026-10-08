import Foundation

/// One GPS reading. Same fields on iPhone, Watch and (later) Android.
public struct GeoFix: Codable, Equatable {
    public var lat: Double
    public var lon: Double
    public var acc: Double          // horizontal accuracy, metres
    public var alt: Double?         // metres, nil when unknown
    public var speed: Double?       // m/s from the GPS chip (Doppler), nil when unknown
    public var t: Double            // milliseconds since 1970
    public init(lat: Double, lon: Double, acc: Double, alt: Double?, speed: Double?, t: Double) {
        self.lat = lat; self.lon = lon; self.acc = acc; self.alt = alt; self.speed = speed; self.t = t
    }
}

/// Running totals for a ski day.
public struct SkiTotals: Codable, Equatable {
    public var distM: Double = 0        // metres skied (lifts excluded)
    public var maxMps: Double = 0
    public var vertM: Double = 0        // metres descended (lifts excluded)
    public var elapsedS: Double = 0     // time with GPS running
    public init() {}
    public init(distM: Double, maxMps: Double, vertM: Double, elapsedS: Double) {
        self.distM = distM; self.maxMps = maxMps; self.vertM = vertM; self.elapsedS = elapsedS
    }
}

/// The ski-day rules shared by every device: smoothing, Doppler-capped distance,
/// standing-still filter, lift detection (with refund of distance counted while boarding),
/// and vertical with 5 m hysteresis. A straight port of the web app's onFix().
public final class SkiEngine {
    public private(set) var totals = SkiTotals()
    public private(set) var speedMps: Double = 0
    public private(set) var onLift = false
    public private(set) var stepDistM: Double = 0

    /// Lift lines of the resort as [[lat, lon]] polylines (for "am I next to a lift?").
    public var liftLines: [[[Double]]] = [] { didSet { indexLifts() } }
    /// The current plan step's line when it is a lift ride, else nil.
    public var plannedLift: [[Double]]?
    /// Flat practice maps (the city): a walk along the bus route is not a lift ride, so need real speed and drop off when slow.
    public var flat = false
    private var slowSince: Double?

    private var lastT: Double?
    private var last: GeoFix?
    private var sm: (lat: Double, lon: Double)?
    private var ema: Double?
    private var prevSp: Double?
    private var altRef: Double?
    private var altHist: [(t: Double, alt: Double)] = []
    private var recent: [(t: Double, d: Double, nearLift: Bool)] = []
    private var grid: [String: [Int]] = [:]

    public init() {}

    /// Continue from totals the user already has today (e.g. tracking was stopped and restarted).
    public func seed(_ t: SkiTotals) { totals = t }
    public func resetStep() { stepDistM = 0 }

    private func slowTooLong(_ p: GeoFix) -> Bool {
        guard flat, let sp = p.speed else { return false }
        if sp >= 1.2 { slowSince = nil; return false }
        if slowSince == nil { slowSince = p.t }
        return p.t - (slowSince ?? p.t) > 45000
    }

    public func ingest(_ p: GeoFix) {
        if let lt = lastT { let g = (p.t - lt) / 1000; if g > 0 && g < 120 { totals.elapsedS += g } }
        lastT = p.t
        let ll = [p.lat, p.lon]
        let good = p.acc <= 30
        let rate = climbingRate(p)
        let nl = nearLift(ll)
        let wasLift = onLift
        var onPlanned = false
        if let pl = plannedLift, pl.count >= 1 {
            onPlanned = SkiEngine.distToLine(ll, pl) < 40 && SkiEngine.hav(ll, pl[0]) > 25
        }
        let moving = (p.speed ?? -1) > (flat ? 3 : 1.5)
        if !onLift {
            onLift = nl < 30 && (((rate ?? -1) > 0.4) || (onPlanned && (moving || (rate == nil && !flat))))
        } else if nl > 60 || (!onPlanned && rate != nil && rate! < 0.1) || slowTooLong(p) {
            onLift = false
        }
        if !onLift && onPlanned && moving && nl < 45 { onLift = true }
        // just boarded: take back the distance counted while walking/queueing at the lift
        if onLift && !wasLift {
            for r in recent where p.t - r.t < 25000 && r.nearLift { totals.distM -= r.d }
            recent.removeAll()
        }
        if good {
            if let s = sm {
                let a = min(0.85, max(0.35, 6 / max(p.acc, 1)))
                sm = (s.lat + (p.lat - s.lat) * a, s.lon + (p.lon - s.lon) * a)
            } else { sm = (p.lat, p.lon) }
        }
        if let l = last, good, let s = sm {
            let dt = (p.t - l.t) / 1000
            let d = SkiEngine.hav([l.lat, l.lon], [s.lat, s.lon])
            if dt > 0 {
                let v = d / dt
                var moved = p; moved.lat = s.lat; moved.lon = s.lon
                let dopplerStill = (p.speed.map { $0 >= 0 && $0 < 0.6 }) ?? false
                if onLift {
                    speedMps = 0; ema = nil; prevSp = nil; stepDistM += d; last = moved
                } else if v < 45 && d > max(3, p.acc * 0.4) && !dopplerStill {
                    // the GPS chip's speed is steadier than position jumps: use it to cap distance
                    let dd = (p.speed.map { $0 >= 0 } ?? false) ? min(d * 1.2, p.speed! * dt + 0.5) : d
                    totals.distM += dd; stepDistM += dd
                    recent.append((p.t, dd, nl < 30))
                    while let f = recent.first, p.t - f.t > 30000 { recent.removeFirst() }
                    let sp = (p.speed.map { $0 >= 0 } ?? false) ? p.speed! : v
                    ema = ema == nil ? sp : ema! * 0.55 + sp * 0.45
                    speedMps = ema!
                    if let ps = prevSp { totals.maxMps = max(totals.maxMps, min(sp, ps)) }
                    prevSp = sp; last = moved
                } else if dt > 4 {
                    ema = (ema ?? 0) * 0.5; speedMps = ema!; prevSp = 0; last = moved
                }
            }
        } else if good || last == nil {
            last = p
            if good { sm = (p.lat, p.lon) }
        }
        if let alt = p.alt, good {
            if onLift { altRef = alt }
            else if let ref = altRef {
                if alt < ref - 5 { totals.vertM += ref - alt; altRef = alt }
                else if alt > ref + 5 { altRef = alt }
            } else { altRef = alt }
        }
    }

    // MARK: helpers (same math as the web app)

    private func climbingRate(_ p: GeoFix) -> Double? {
        guard let alt = p.alt else { return nil }
        altHist.append((p.t, alt))
        while let f = altHist.first, p.t - f.t > 30000 { altHist.removeFirst() }
        guard altHist.count >= 3, let f = altHist.first, p.t - f.t >= 8000 else { return nil }
        return (alt - f.alt) / ((p.t - f.t) / 1000)
    }

    private static func key(_ lat: Double, _ lon: Double, _ dx: Int = 0, _ dy: Int = 0) -> String {
        "\(Int((lat * 200).rounded(.down)) + dx):\(Int((lon * 150).rounded(.down)) + dy)"
    }

    private func indexLifts() {
        grid = [:]
        for (i, line) in liftLines.enumerated() {
            var keys = Set<String>()
            for p in line where p.count == 2 { keys.insert(SkiEngine.key(p[0], p[1])) }
            // long lifts: also index points along each segment
            for j in 0..<max(0, line.count - 1) {
                let a = line[j], b = line[j + 1]
                let n = max(1, Int(SkiEngine.hav(a, b) / 150))
                for k in 0...n { keys.insert(SkiEngine.key(a[0] + (b[0] - a[0]) * Double(k) / Double(n), a[1] + (b[1] - a[1]) * Double(k) / Double(n))) }
            }
            for k in keys { grid[k, default: []].append(i) }
        }
    }

    private func nearLift(_ p: [Double]) -> Double {
        // no lift map loaded (e.g. on the watch): treat every climb as a possible lift, decided by climb rate alone
        if liftLines.isEmpty { return 0 }
        var best = 1e9
        var seen = Set<Int>()
        for dx in -1...1 { for dy in -1...1 {
            guard let s = grid[SkiEngine.key(p[0], p[1], dx, dy)] else { continue }
            for li in s where !seen.contains(li) { seen.insert(li); best = min(best, SkiEngine.distToLine(p, liftLines[li])) }
        } }
        return best
    }

    public static func hav(_ a: [Double], _ b: [Double]) -> Double {
        let t = Double.pi / 180, dLa = (b[0] - a[0]) * t, dLo = (b[1] - a[1]) * t
        let s = pow(sin(dLa / 2), 2) + cos(a[0] * t) * cos(b[0] * t) * pow(sin(dLo / 2), 2)
        return 2 * 6371000 * asin(min(1, sqrt(s)))
    }

    static func distToLine(_ p: [Double], _ c: [[Double]]) -> Double {
        guard c.count >= 2 else { return c.isEmpty ? 1e9 : hav(p, c[0]) }
        var m = 1e9
        for i in 0..<(c.count - 1) { m = min(m, distToSeg(p, c[i], c[i + 1])) }
        return m
    }

    private static func distToSeg(_ p: [Double], _ a: [Double], _ b: [Double]) -> Double {
        let k = cos(p[0] * Double.pi / 180)   // local scale (the web app fixes this at 46.2°)
        func xy(_ q: [Double]) -> (Double, Double) { (q[1] * 111320 * k, q[0] * 110540) }
        let P = xy(p), A = xy(a), B = xy(b)
        let dx = B.0 - A.0, dy = B.1 - A.1, L = dx * dx + dy * dy
        var t = L > 0 ? ((P.0 - A.0) * dx + (P.1 - A.1) * dy) / L : 0
        t = max(0, min(1, t))
        return hypot(P.0 - (A.0 + t * dx), P.1 - (A.1 + t * dy))
    }
}
