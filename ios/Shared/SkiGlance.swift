import Foundation

/// Everything a glance shows (lock screen, Dynamic Island, watch, Smart Stack), computed in one place
/// so the phone, the widgets and the watch never disagree.
struct SkiGlance: Codable, Hashable {
    var speedKmh = 0
    var km = 0.0
    var maxKmh = 0
    var vertM = 0
    var onLift = false
    var run = ""                 // what you're on now: "Chaux Fleuries"
    var runColor = "lift"        // blue, red, black, green, lift, end
    var nextLift = ""            // "Ardent gondola"
    var nextLiftM = -1           // metres to the bottom of the next lift, -1 = unknown
    var liftName = ""            // on a lift: which one (empty when it isn't one from the plan)
    var liftProgress = 0.0       // 0...1 up the planned lift
    var liftMin = 0              // minutes to the top, 0 = unknown
    var then = ""                // the step after this one
    var thenColor = "lift"

    /// The plan step the phone (or watch) is on, with the bits a glance needs.
    struct Step {
        var label: String
        var color: String
        var ends: [[Double]]?     // [start, end] of this step
        var nextLift: String
        var nextLiftAt: [Double]?
        var then: String
        var thenColor: String
    }

    static func make(speedMps: Double, totals: SkiTotals, onLift: Bool, at pos: [Double]?, step: Step?) -> SkiGlance {
        var g = SkiGlance()
        g.speedKmh = Int((speedMps * 3.6).rounded())
        g.km = totals.distM / 1000
        g.maxKmh = Int((totals.maxMps * 3.6).rounded())
        g.vertM = Int(totals.vertM.rounded())
        g.onLift = onLift
        guard let s = step else {
            if onLift { g.run = "Lift" }
            return g
        }
        let stepIsLift = s.color == "lift"
        g.run = SkiText.short(s.label)
        g.runColor = s.color
        g.nextLift = SkiText.short(s.nextLift)
        g.then = SkiText.short(s.then)
        g.thenColor = s.thenColor
        if let p = pos, let at = s.nextLiftAt {
            let d = SkiText.hav(p, at)
            g.nextLiftM = d.isFinite ? Int(d) : -1
        }
        if onLift {
            if stepIsLift, let e = s.ends, e.count == 2 {
                // riding the planned lift
                g.liftName = g.run
                if let p = pos {
                    let (done, mins) = SkiText.liftProgress(at: p, start: e[0], end: e[1])
                    g.liftProgress = done; g.liftMin = mins
                }
            } else {
                // a lift that isn't the planned one: say so, no made-up progress
                g.liftName = ""
                g.run = "Lift"; g.runColor = "lift"
            }
        }
        return g
    }

    /// "then Ardent gondola" line: on a run it's the next lift, on a lift it's the next run.
    var upNext: String {
        if onLift { return then.isEmpty ? "" : then }
        return nextLift
    }
}
