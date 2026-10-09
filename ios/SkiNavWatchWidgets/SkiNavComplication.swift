import SwiftUI
import WidgetKit

/// Watch face complication. One complication that follows the day by itself:
/// countdown before the trip, the plan on trip mornings, live speed / run / next lift while skiing,
/// minutes to the top on a lift, and the day's totals when done. The watch app saves what to show
/// (SkiFace, in the shared app group) and asks for a refresh when it changes.
@main
struct SkiNavComplications: WidgetBundle {
    var body: some Widget { SkiNavComplication() }
}

struct FaceEntry: TimelineEntry {
    let date: Date
    let face: SkiFace
}

struct FaceProvider: TimelineProvider {
    func placeholder(in context: Context) -> FaceEntry { FaceEntry(date: SkiFace.tripStart, face: SkiFace()) }
    func getSnapshot(in context: Context, completion: @escaping (FaceEntry) -> Void) { completion(FaceEntry(date: .now, face: SkiFace.load())) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<FaceEntry>) -> Void) {
        let face = SkiFace.load()
        let cal = Calendar.current
        let now = Date()
        var dates = [now]
        // live numbers go stale after 15 min without news: switch to the morning / done view then
        if face.tracking { dates.append(face.updated.addingTimeInterval(15 * 60 + 5)) }
        // 6 pm (après ends) and the next midnights (new day, countdown)
        if let six = cal.date(bySettingHour: 18, minute: 0, second: 5, of: now), six > now { dates.append(six) }
        let midnight = cal.startOfDay(for: now)
        for i in 1...3 { if let d = cal.date(byAdding: .day, value: i, to: midnight) { dates.append(d.addingTimeInterval(5)) } }
        let entries = dates.filter { $0 >= now }.sorted().map { FaceEntry(date: $0, face: face) }
        completion(Timeline(entries: entries, policy: .after(now.addingTimeInterval(30 * 60))))
    }
}

struct SkiNavComplication: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: SkiFace.kind, provider: FaceProvider()) { e in
            ComplicationView(c: e.face.content(at: e.date)).containerBackground(.black, for: .widget)
        }
        .configurationDisplayName("Ski Nav")
        .description("Your ski day: the plan, live speed and run, lifts, and the day's totals.")
        .supportedFamilies([.accessoryCircular, .accessoryCorner, .accessoryRectangular, .accessoryInline])
    }
}

struct ComplicationView: View {
    @Environment(\.widgetFamily) private var family
    let c: SkiFace.Content
    var body: some View {
        switch family {
        case .accessoryCircular: FaceRing(c: c)
        case .accessoryCorner: FaceCorner(c: c)
        case .accessoryInline: FaceInline(c: c)
        default: FaceRect(c: c)
        }
    }
}
