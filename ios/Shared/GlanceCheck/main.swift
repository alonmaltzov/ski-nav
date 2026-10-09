import Foundation
// Checks what the glances show, using the real plan labels. Prints one JSON line per check.
func check(_ name: String, _ ok: Bool, _ detail: String) {
    let d = detail.replacingOccurrences(of: "\"", with: "'")
    print("[web] QA RESULT {\"check\":\"glance: \(name)\",\"ok\":\(ok),\"detail\":\"\(d)\"}")
}
let shorts: [(String, String)] = [
    ("Ski Chaux Fleuries (red) → Grand Plan (blue) → Parchets (blue)", "Chaux Fleuries"),
    ("Take Ardent gondola", "Ardent gondola"),
    ("Traverse to Chaux Fleurie chair", "Chaux Fleurie chair"),
    ("Ski Proclou (green)", "Proclou"),
]
for (a, b) in shorts { check("short name '\(b)'", SkiText.short(a) == b, SkiText.short(a)) }
var t = SkiTotals(); t.distM = 12_400; t.maxMps = 15; t.vertM = 1840
let run = SkiGlance.Step(label: "Ski Chaux Fleuries (red) → Grand Plan (blue)", color: "red", ends: [[46.21169, 6.79035], [46.21378, 6.76099]],
                         nextLift: "Take Ardent gondola", nextLiftAt: [46.21378, 6.76099], then: "Take Ardent gondola", thenColor: "lift")
let g = SkiGlance.make(speedMps: 42 / 3.6, totals: t, onLift: false, at: [46.2125, 6.7800], step: run)
check("skiing", g.speedKmh == 42 && g.run == "Chaux Fleuries" && g.nextLift == "Ardent gondola" && g.nextLiftM > 1000 && g.nextLiftM < 2000,
      "\(g.speedKmh) km/h \(g.run) next \(g.nextLift) \(g.nextLiftM) m")
let lift = SkiGlance.Step(label: "Take Ardent gondola", color: "lift", ends: [[46.21378, 6.76099], [46.20792, 6.77813]],
                          nextLift: "Take Chaux Fleurie chair", nextLiftAt: [46.20701, 6.77827], then: "Ski Parchets (blue)", thenColor: "blue")
let l = SkiGlance.make(speedMps: 5, totals: t, onLift: true, at: [46.2100, 6.7710], step: lift)
check("planned lift", l.liftName == "Ardent gondola" && l.liftProgress > 0.3 && l.liftProgress < 0.8 && l.liftMin >= 1 && l.then == "Parchets",
      "\(l.liftName) \(Int(l.liftProgress * 100))% \(l.liftMin) min then \(l.then)")
let u = SkiGlance.make(speedMps: 5, totals: t, onLift: true, at: [46.2125, 6.7800], step: run)
check("unplanned lift", u.run == "Lift" && u.liftName.isEmpty && u.liftMin == 0, "\(u.run) '\(u.liftName)' \(u.liftMin)")
let n = SkiGlance.make(speedMps: 10, totals: t, onLift: false, at: nil, step: nil)
check("no plan", n.run.isEmpty && n.speedKmh == 36, "\(n.speedKmh) '\(n.run)'")
let rt = try! JSONDecoder().decode(SkiGlance.self, from: JSONEncoder().encode(l))
check("phone to watch round trip", rt == l, "\(try! JSONEncoder().encode(l).count) bytes")

faceChecks()
