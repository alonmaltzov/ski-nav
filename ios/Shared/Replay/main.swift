import Foundation
// Replays a GPX file through SkiEngine and prints the day's totals as JSON.
// usage: replay <track.gpx> <lifts.json> [steps.json: [[fixIndex, liftLine|null], ...] from the web app]
let args = CommandLine.arguments
let gpx = try! String(contentsOfFile: args[1], encoding: .utf8)
let lifts = try! JSONDecoder().decode([[[Double]]].self, from: Data(contentsOf: URL(fileURLWithPath: args[2])))
let re = try! NSRegularExpression(pattern: #"lat="([-\d.]+)"\s+lon="([-\d.]+)">\s*<ele>([-\d.]+)</ele>\s*<time>([^<]+)</time>"#)
let fmt = ISO8601DateFormatter()
let engine = SkiEngine()
engine.liftLines = lifts
var n = 0, liftFixes = 0
var stepChanges: [Int: [[Double]]?] = [:]
if args.count > 3, let arr = try? JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: args[3]))) as? [[Any]] {
    for e in arr { if let i = e[0] as? Int { stepChanges[i] = (e[1] as? [[Double]]) } }
}
for m in re.matches(in: gpx, range: NSRange(gpx.startIndex..., in: gpx)) {
    func g(_ i: Int) -> String { String(gpx[Range(m.range(at: i), in: gpx)!]) }
    guard let date = fmt.date(from: g(4)) else { continue }
    if let c = stepChanges[n] { engine.plannedLift = c }
    engine.ingest(GeoFix(lat: Double(g(1))!, lon: Double(g(2))!, acc: 5, alt: Double(g(3))!, speed: nil, t: date.timeIntervalSince1970 * 1000))
    n += 1; if engine.onLift { liftFixes += 1 }
}
let t = engine.totals
print(String(format: #"{"fixes":%d,"km":%.2f,"maxKmh":%.1f,"vertM":%.0f,"hours":%.2f,"liftFixes":%d}"#, n, t.distM / 1000, t.maxMps * 3.6, t.vertM, t.elapsedS / 3600, liftFixes))
