import ActivityKit
import SwiftUI
import WidgetKit

@main
struct SkiNavWidgets: WidgetBundle {
    var body: some Widget { SkiDayLiveActivity() }
}

private func tint(_ c: String) -> Color {
    switch c {
    case "blue": return Color(red: 0.11, green: 0.37, blue: 0.88)
    case "red": return Color(red: 0.85, green: 0.12, blue: 0.15)
    case "black": return .primary
    case "green": return Color(red: 0.09, green: 0.64, blue: 0.29)
    case "end": return Color(red: 1.0, green: 0.35, blue: 0.12)
    default: return .gray
    }
}

struct SkiDayLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: SkiActivityAttributes.self) { ctx in
            // lock screen
            let s = ctx.state
            VStack(alignment: .leading, spacing: 8) {
                HStack(alignment: .firstTextBaseline) {
                    Text("\(s.speedKmh)").font(.system(size: 44, weight: .bold, design: .rounded)).monospacedDigit()
                        .foregroundStyle(s.onLift ? .secondary : .primary)
                    Text(s.onLift ? "LIFT" : "km/h").font(.caption.bold()).foregroundStyle(.secondary)
                    Spacer()
                    Text(ctx.attributes.startedAt, style: .timer).font(.title3.monospacedDigit()).multilineTextAlignment(.trailing)
                }
                HStack {
                    stat(String(format: "%.1f", s.km), "km")
                    stat("\(s.maxKmh)", "max")
                    stat("\(s.vertM)", "vert m")
                }
                HStack(spacing: 6) {
                    RoundedRectangle(cornerRadius: 3).fill(tint(s.stepColor)).frame(width: 6, height: 18)
                    Text(s.step).font(.subheadline.weight(.semibold)).lineLimit(1)
                }
            }
            .padding(16)
            .activityBackgroundTint(Color(.systemBackground).opacity(0.85))
        } dynamicIsland: { ctx in
            let s = ctx.state
            return DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    VStack(alignment: .leading) {
                        Text("\(s.speedKmh)").font(.title.bold()).monospacedDigit()
                        Text(s.onLift ? "on lift" : "km/h").font(.caption2).foregroundStyle(.secondary)
                    }
                }
                DynamicIslandExpandedRegion(.trailing) {
                    VStack(alignment: .trailing) {
                        Text(String(format: "%.1f km", s.km)).font(.headline).monospacedDigit()
                        Text("max \(s.maxKmh)").font(.caption2).foregroundStyle(.secondary)
                    }
                }
                DynamicIslandExpandedRegion(.bottom) {
                    Text(s.step).font(.subheadline).lineLimit(1).foregroundStyle(tint(s.stepColor))
                }
            } compactLeading: {
                Text("\(s.speedKmh)").monospacedDigit().foregroundStyle(s.onLift ? .secondary : .primary)
            } compactTrailing: {
                Text(String(format: "%.1f", s.km)).monospacedDigit()
            } minimal: {
                Text("\(s.speedKmh)").monospacedDigit()
            }
        }
    }

    private func stat(_ v: String, _ label: String) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(v).font(.title3.weight(.semibold)).monospacedDigit()
            Text(label).font(.caption2).foregroundStyle(.secondary)
        }.frame(maxWidth: .infinity, alignment: .leading)
    }
}
