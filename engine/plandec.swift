import Foundation
/// One step of today's plan, as sent by the phone.
struct PlanStep: Codable, Identifiable {
    var id: Int { idx }
    var idx: Int = 0
    let l: String        // label, e.g. "Take Prolays chair"
    let t: String        // "run" | "lift" | "end"
    let c: String        // colour: blue, red, black, green, lift, end
    let len: Double
    let s: [Double]      // start [lat, lon]
    let e: [Double]      // end [lat, lon]
    let at: String
    init(l: String, t: String, c: String, len: Double, s: [Double], e: [Double], at: String) {
        self.l = l; self.t = t; self.c = c; self.len = len; self.s = s; self.e = e; self.at = at
    }
    // idx is set on the watch after decoding, the phone doesn't send it
    enum CodingKeys: String, CodingKey { case l, t, c, len, s, e, at }
}

struct Plan: Codable {
    let day: Int
    let title: String
    var steps: [PlanStep]
}
for f in CommandLine.arguments.dropFirst() {
    do { let p = try JSONDecoder().decode(Plan.self, from: try Data(contentsOf: URL(fileURLWithPath: f))); print("OK \(p.steps.count)") }
    catch { print("FAIL \(error)") }
}
