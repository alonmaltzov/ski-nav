import SwiftUI
import WidgetKit

/// Watch face complication: one tap from the face into Ski Nav, plus where you are in the trip.
/// Live speed and run on the wrist come from the iPhone's Live Activity in the Smart Stack
/// (and from the app itself, which stays in front during a ski workout).
@main
struct SkiNavComplications: WidgetBundle {
    var body: some Widget { SkiNavComplication() }
}

struct TripEntry: TimelineEntry {
    let date: Date
    let line: String     // "Day 1 of 6", "In 12 days", "Trip done"
    let short: String    // "D1", "12d", ""
}

enum Trip {
    // Avoriaz: ski days Sun Jan 17 to Fri Jan 22, 2027
    static let firstDay = DateComponents(calendar: .current, year: 2027, month: 1, day: 17).date!
    static let days = 6

    static func entry(_ d: Date) -> TripEntry {
        let cal = Calendar.current
        let n = cal.dateComponents([.day], from: cal.startOfDay(for: firstDay), to: cal.startOfDay(for: d)).day ?? 0
        if n < 0 { return .init(date: d, line: "Avoriaz in \(-n) day\(n == -1 ? "" : "s")", short: "\(-n)d") }
        if n < days { return .init(date: d, line: "Day \(n + 1) of \(days)", short: "D\(n + 1)") }
        return .init(date: d, line: "Ski Nav", short: "")
    }
}

struct TripProvider: TimelineProvider {
    func placeholder(in context: Context) -> TripEntry { Trip.entry(Trip.firstDay) }
    func getSnapshot(in context: Context, completion: @escaping (TripEntry) -> Void) { completion(Trip.entry(.now)) }
    func getTimeline(in context: Context, completion: @escaping (Timeline<TripEntry>) -> Void) {
        // one entry per midnight for the next week
        let cal = Calendar.current
        let today = cal.startOfDay(for: .now)
        let entries = (0..<7).compactMap { cal.date(byAdding: .day, value: $0, to: today) }.map { Trip.entry($0 == today ? .now : $0) }
        completion(Timeline(entries: entries, policy: .atEnd))
    }
}

struct SkiNavComplication: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: "SkiNavComplication", provider: TripProvider()) { e in
            ComplicationView(e: e).containerBackground(.black, for: .widget)
        }
        .configurationDisplayName("Ski Nav")
        .description("Open Ski Nav from your watch face.")
        .supportedFamilies([.accessoryCircular, .accessoryCorner, .accessoryRectangular, .accessoryInline])
    }
}

struct ComplicationView: View {
    @Environment(\.widgetFamily) private var family
    let e: TripEntry
    private let accent = Color(red: 1.0, green: 0.54, blue: 0.24)

    var body: some View {
        switch family {
        case .accessoryCircular:
            ZStack {
                AccessoryWidgetBackground()
                VStack(spacing: 0) {
                    Image(systemName: "figure.skiing.downhill").font(.title3.weight(.semibold))
                    if !e.short.isEmpty { Text(e.short).font(.caption2.weight(.bold)).widgetAccentable() }
                }
            }
            .accessibilityLabel("Ski Nav, \(e.line)")
        case .accessoryCorner:
            Image(systemName: "figure.skiing.downhill").font(.title2.weight(.semibold))
                .widgetLabel { Text(e.line) }
                .accessibilityLabel("Ski Nav, \(e.line)")
        case .accessoryInline:
            Label(e.line == "Ski Nav" ? "Ski Nav" : "Ski Nav · \(e.line)", systemImage: "figure.skiing.downhill")
        default:
            HStack(spacing: 8) {
                Image(systemName: "figure.skiing.downhill").font(.title2.weight(.semibold)).foregroundStyle(accent).widgetAccentable()
                VStack(alignment: .leading, spacing: 0) {
                    Text("SKI NAV").font(.caption2.weight(.bold)).foregroundStyle(accent).widgetAccentable()
                    Text(e.line).font(.headline).lineLimit(1)
                    Text("Tap for speed, run, next lift").font(.caption2).foregroundStyle(.secondary).lineLimit(1)
                }
                Spacer(minLength: 0)
            }
            .accessibilityElement(children: .combine)
        }
    }
}
