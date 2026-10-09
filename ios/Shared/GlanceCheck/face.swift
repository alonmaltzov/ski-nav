import Foundation
// Checks what the watch face complication says in each part of the day.
func faceChecks() {
    let cal = Calendar.current
    let day3 = cal.date(byAdding: .day, value: 2, to: SkiFace.tripStart)!
    func at(_ h: Int, _ m: Int, _ d: Date = day3) -> Date { cal.date(bySettingHour: h, minute: m, second: 0, of: d)! }
    var f = SkiFace(); f.dayKey = SkiFace.key(day3); f.day = 3; f.title = "Châtel side"; f.kmPlan = 24; f.firstAt = "9:15"; f.firstLift = "Proclou chair"

    let m = f.content(at: at(8, 42))
    check("face: trip morning", m.mode == .morning && m.title == "Châtel side" && m.sub1 == "24 km planned · first lift 9:15" && m.corner == "DAY 3", "\(m.mode) \(m.title) | \(m.sub1) | \(m.corner)")

    var s = f; s.tracking = true; s.updated = at(10, 41)
    s.g.speedKmh = 42; s.g.km = 12.4; s.g.run = "Chaux Fleuries"; s.g.runColor = "red"; s.g.nextLift = "Ardent gondola"; s.g.nextLiftM = 1200
    let k = s.content(at: at(10, 42))
    check("face: skiing", k.mode == .skiing && k.ringCenter == "42" && k.top == "ON A RED" && k.topRight == "12.4 of 24 km" && k.sub1 == "Next lift: Ardent gondola · 1.2 km" && abs(k.ring - 12.4 / 24) < 0.01,
          "\(k.ringCenter) \(k.top) \(k.topRight) \(k.sub1)")

    var l = s; l.g.onLift = true; l.g.liftName = "Ardent gondola"; l.g.liftMin = 4; l.g.liftProgress = 0.6; l.g.then = "Lindarets"; l.g.thenColor = "blue"
    let lc = l.content(at: at(10, 42))
    check("face: on a lift", lc.mode == .lift && lc.ringCenter == "4" && lc.topRight == "top in 4 min" && lc.sub1 == "Then: Lindarets, blue", "\(lc.ringCenter) \(lc.topRight) \(lc.sub1)")

    let stale = s.content(at: at(11, 0))
    check("face: live numbers go stale after 15 min", stale.mode == .done, "\(stale.mode)")

    var d = s; d.tracking = false; d.g.km = 26.1; d.g.vertM = 3400; d.g.maxKmh = 61
    let dc = d.content(at: at(15, 20))
    check("face: day done", dc.mode == .done && dc.title == "Folie Douce till 6" && dc.topRight == "26.1 km" && dc.sub2 == "Tomorrow: Day 4", "\(dc.title) \(dc.topRight) \(dc.sub2)")

    let before = SkiFace().content(at: cal.date(byAdding: .day, value: -10, to: SkiFace.tripStart)!)
    check("face: countdown", before.mode == .countdown && before.title == "Avoriaz in 10 days", before.title)

    let nextDay = d.content(at: at(8, 30, cal.date(byAdding: .day, value: 1, to: day3)!))
    check("face: yesterday's totals don't show the next morning", nextDay.mode == .morning, "\(nextDay.mode)")

    let rt = try! JSONDecoder().decode(SkiFace.self, from: JSONEncoder().encode(l))
    check("face: save round trip", rt == l, "")
}
