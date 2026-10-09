import Foundation

/// What the watch face complication shows, saved by the watch app in the shared app group and read by the
/// complication. One complication that changes with the day by itself: countdown, trip morning, skiing,
/// on a lift, day done.
struct SkiFace: Codable, Equatable {
    var updated = Date.distantPast
    var tracking = false          // the numbers are live (watch workout or phone tracking)
    var dayKey = ""               // yyyy-MM-dd the totals belong to
    var day = 0                   // plan day number
    var title = ""                // plan title, "Avoriaz north + Lindarets"
    var kmPlan = 0.0              // km of runs planned today
    var firstAt = ""              // "9:15"
    var firstLift = ""            // "Proclou chair"
    var g = SkiGlance()           // latest numbers

    static let group = "group.com.alonmaltzov.SkiNav"
    static let kind = "SkiNavComplication"
    // ski days: Sun Jan 17 to Fri Jan 22, 2027
    static let tripStart = DateComponents(calendar: Calendar(identifier: .gregorian), year: 2027, month: 1, day: 17).date!
    static let tripDays = 6
    static let endName = "Folie Douce"

    static func key(_ d: Date) -> String {
        let c = Calendar.current.dateComponents([.year, .month, .day], from: d)
        return String(format: "%04d-%02d-%02d", c.year ?? 0, c.month ?? 0, c.day ?? 0)
    }

    static func load() -> SkiFace {
        guard let d = UserDefaults(suiteName: group)?.data(forKey: "face"), let f = try? JSONDecoder().decode(SkiFace.self, from: d) else { return SkiFace() }
        return f
    }
    func save() {
        if let d = try? JSONEncoder().encode(self) { UserDefaults(suiteName: SkiFace.group)?.set(d, forKey: "face") }
    }

    /// Trip day index for a date: <0 before the trip, 0...5 during, >=6 after.
    static func tripIndex(_ now: Date) -> Int {
        let cal = Calendar.current
        return cal.dateComponents([.day], from: cal.startOfDay(for: tripStart), to: cal.startOfDay(for: now)).day ?? 0
    }

    enum Mode: String { case countdown, morning, skiing, lift, done, idle }

    /// Everything the four complication sizes need, worked out once.
    struct Content: Equatable {
        var mode: Mode
        var ring = 0.0, ringCenter = "", ringUnit = "", ringCheck = false
        var top = "", topRight = "", title = "", titleColor = ""   // titleColor: run colour for the bar, "" = none
        var bar: Double? = nil, barWhite = false
        var sub1 = "", sub2 = ""
        var corner = "", inline = ""
    }

    func content(at now: Date) -> Content {
        let n = SkiFace.tripIndex(now)
        let today = dayKey == SkiFace.key(now)
        let live = tracking && today && now.timeIntervalSince(updated) < 15 * 60
        let dayNo = day > 0 ? day : n + 1
        let kmTxt = String(format: "%.1f", g.km)
        let planKm = kmPlan > 0 ? "\(Int(kmPlan.rounded()))" : ""

        if live && g.onLift {
            var c = Content(mode: .lift)
            let name = g.liftName.isEmpty ? "Lift" : g.liftName
            c.ring = g.liftProgress; c.ringCenter = g.liftMin > 0 ? "\(g.liftMin)" : "–"; c.ringUnit = "MIN"
            c.top = "ON A LIFT"; c.topRight = g.liftMin > 0 ? "top in \(g.liftMin) min" : "\(kmTxt) km"
            c.title = name; c.bar = g.liftName.isEmpty ? nil : g.liftProgress; c.barWhite = true
            c.sub1 = g.then.isEmpty ? "\(kmTxt) km today" : "Then: \(g.then), \(SkiText.colorWord(g.thenColor).lowercased())"
            c.corner = g.liftMin > 0 ? "TOP IN \(g.liftMin) MIN" : "ON A LIFT"
            c.inline = g.liftMin > 0 ? "\(name) · top in \(g.liftMin) min" : "On \(name)"
            return c
        }
        if live {
            var c = Content(mode: .skiing)
            c.ring = kmPlan > 0 ? min(1, g.km / kmPlan) : 0; c.ringCenter = "\(g.speedKmh)"; c.ringUnit = "KM/H"
            let colored = ["blue", "red", "black", "green"].contains(g.runColor)
            c.top = colored ? "ON A \(g.runColor.uppercased())" : "SKIING"
            c.topRight = kmPlan > 0 ? "\(kmTxt) of \(planKm) km" : "\(kmTxt) km"
            c.title = g.run.isEmpty ? "Skiing" : g.run; c.titleColor = colored ? g.runColor : ""
            c.bar = kmPlan > 0 ? min(1, g.km / kmPlan) : nil
            if !g.nextLift.isEmpty {
                c.sub1 = "Next lift: \(g.nextLift)" + (g.nextLiftM >= 0 ? " · \(SkiText.km(Double(g.nextLiftM)))" : "")
            } else { c.sub1 = "max \(g.maxKmh) km/h · \(g.vertM) m down" }
            c.corner = kmPlan > 0 ? "\(kmTxt) / \(planKm) KM" : "\(kmTxt) KM"
            c.inline = "\(g.speedKmh) km/h" + (g.run.isEmpty ? "" : " · \(g.run)")
            return c
        }
        if today && g.km > 0.2 {
            var c = Content(mode: .done)
            c.ring = 1; c.ringCheck = true
            let tripDay = n >= 0 && n < SkiFace.tripDays
            c.top = tripDay ? "DAY \(dayNo) DONE" : "DAY DONE"; c.topRight = "\(kmTxt) km"
            c.title = tripDay && now < Calendar.current.date(bySettingHour: 18, minute: 0, second: 0, of: now)! ? "\(SkiFace.endName) till 6" : "Nice skiing"
            c.sub1 = "\(g.vertM.formatted()) m down · max \(g.maxKmh) km/h"
            c.sub2 = tripDay && n + 1 < SkiFace.tripDays ? "Tomorrow: Day \(n + 2)" : ""
            c.corner = tripDay ? "DAY \(dayNo) DONE" : "\(kmTxt) KM"
            c.inline = (tripDay ? "Day \(dayNo) done" : "Day done") + " · \(kmTxt) km"
            return c
        }
        if n >= 0 && n < SkiFace.tripDays {
            var c = Content(mode: .morning)
            let d = n + 1
            let planned = day == d
            c.ring = 0; c.ringCenter = planned && kmPlan > 0 ? planKm : "D\(d)"; c.ringUnit = planned && kmPlan > 0 ? "KM PLAN" : "DAY"
            c.top = "SKI NAV · DAY \(d)"; c.topRight = planned && !firstAt.isEmpty ? "skis on \(firstAt)" : ""
            c.title = planned && !title.isEmpty ? title : "Day \(d) of \(SkiFace.tripDays)"
            c.sub1 = planned && kmPlan > 0 ? "\(planKm) km planned" + (firstAt.isEmpty ? "" : " · first lift \(firstAt)") : "Open Ski Nav for today's plan"
            c.sub2 = planned && !firstLift.isEmpty ? "First: \(firstLift)" : ""
            c.corner = "DAY \(d)"
            c.inline = "Ski Nav · Day \(d)" + (planned && kmPlan > 0 ? " · \(planKm) km" : "")
            return c
        }
        if n < 0 {
            var c = Content(mode: .countdown)
            let left = -n
            c.ring = max(0, 1 - Double(left) / 100); c.ringCenter = "\(left)"; c.ringUnit = left == 1 ? "DAY" : "DAYS"
            c.top = "SKI NAV"; c.title = "Avoriaz in \(left) day\(left == 1 ? "" : "s")"
            c.sub1 = "Skis on: Sun Jan 17"
            c.corner = "AVORIAZ IN \(left)D"
            c.inline = "Avoriaz in \(left) day\(left == 1 ? "" : "s")"
            return c
        }
        var c = Content(mode: .idle)
        c.ringCenter = "⛷"; c.top = "SKI NAV"; c.title = "Ski Nav"; c.sub1 = "Tap to open"; c.corner = "SKI NAV"; c.inline = "Ski Nav"
        return c
    }
}
