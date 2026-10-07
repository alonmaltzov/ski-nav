import ActivityKit
import SwiftUI
import WidgetKit

@main
struct SkiNavWidgets: WidgetBundle {
    var body: some Widget { SkiDayLiveActivity() }
}

/// The ski day on the lock screen, in the Dynamic Island and (iOS 18+) in the Apple Watch Smart Stack.
struct SkiDayLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: SkiActivityAttributes.self) { ctx in
            LiveActivityRoot(g: ctx.state)
                .activityBackgroundTint(Color(red: 0.03, green: 0.05, blue: 0.06).opacity(0.88))
                .activitySystemActionForegroundColor(.white)
        } dynamicIsland: { ctx in
            let g = ctx.state
            return DynamicIsland {
                DynamicIslandExpandedRegion(.bottom) {
                    VStack(spacing: 10) {
                        IslandExpandedTop(g: g)
                        NowRow(g: g, nameSize: 22)
                    }
                    .padding(.horizontal, 6)
                    .accessibilityElement(children: .ignore)
                    .accessibilityLabel(g.spoken)
                }
            } compactLeading: {
                IslandCompactLeading(g: g)
            } compactTrailing: {
                IslandCompactTrailing(g: g)
            } minimal: {
                if g.onLift { Image(systemName: "cablecar.fill") } else { Text("\(g.speedKmh)").font(SkiStyle.big(17)).monospacedDigit() }
            }
            .keylineTint(SkiStyle.fill(g.runColor))
        }
        .supplementalActivityFamilies([.small, .medium])
    }
}

/// Lock screen (.medium) or the smaller watch Smart Stack (.small).
struct LiveActivityRoot: View {
    @Environment(\.activityFamily) private var family
    let g: SkiGlance
    var body: some View {
        switch family {
        case .small: WatchStackGlance(g: g).padding(4)
        default: LockScreenGlance(g: g)
        }
    }
}
