#if os(iOS)
import SwiftUI

/// Lock screen Live Activity: speed, km, what you're on, what's next. Nothing else.
struct LockScreenGlance: View {
    let g: SkiGlance
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .firstTextBaseline) {
                HStack(alignment: .firstTextBaseline, spacing: 4) {
                    Text("\(g.speedKmh)").font(SkiStyle.big(64)).monospacedDigit()
                        .foregroundStyle(g.onLift ? SkiStyle.muted : .white)
                    Text("km/h").font(.subheadline.bold()).foregroundStyle(SkiStyle.muted)
                }
                Spacer()
                Text(String(format: "%.1f km", g.km)).font(SkiStyle.big(30)).monospacedDigit().foregroundStyle(.white)
            }
            NowRow(g: g)
        }
        .padding(.horizontal, 18).padding(.vertical, 14)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(g.spoken)
    }
}

/// "▍Chaux Fleuries      then Ardent gondola", or on a lift "🚡 Ardent gondola   top in 3 min".
struct NowRow: View {
    let g: SkiGlance
    var nameSize: CGFloat = 24
    var body: some View {
        HStack(spacing: 10) {
            if g.onLift {
                Image(systemName: "cablecar.fill").font(.title3).foregroundStyle(.white)
                Text(g.liftName.isEmpty ? "On a lift" : g.liftName)
                    .font(SkiStyle.big(nameSize)).foregroundStyle(.white).lineLimit(1)
                Spacer(minLength: 4)
                if g.liftMin > 0 {
                    Text("top in \(g.liftMin) min").font(.subheadline.weight(.semibold)).foregroundStyle(SkiStyle.muted).lineLimit(1)
                }
            } else {
                RunBar(color: g.runColor, height: nameSize + 6)
                Text(g.run.isEmpty ? "Free skiing" : g.run)
                    .font(SkiStyle.big(nameSize)).foregroundStyle(.white).lineLimit(1).minimumScaleFactor(0.8)
                Spacer(minLength: 4)
                if !g.nextLift.isEmpty {
                    Text("then \(g.nextLift)").font(.subheadline.weight(.semibold)).foregroundStyle(SkiStyle.muted)
                        .lineLimit(1).minimumScaleFactor(0.8)
                }
            }
        }
    }
}

/// Expanded Dynamic Island: big speed, km with max and vertical, then the same "now" row.
struct IslandExpandedTop: View {
    let g: SkiGlance
    var body: some View {
        HStack(alignment: .bottom) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text("\(g.speedKmh)").font(SkiStyle.big(52)).monospacedDigit().foregroundStyle(g.onLift ? SkiStyle.muted : .white)
                Text("km/h").font(.caption.bold()).foregroundStyle(SkiStyle.muted)
            }
            Spacer()
            VStack(alignment: .trailing, spacing: 0) {
                Text(String(format: "%.1f km", g.km)).font(SkiStyle.big(26)).monospacedDigit()
                Text("max \(g.maxKmh) · \(g.vertM.formatted()) m").font(.caption.weight(.semibold)).foregroundStyle(SkiStyle.muted)
            }
        }
    }
}

/// Compact island, leading side: run colour + speed, or a lift icon.
struct IslandCompactLeading: View {
    let g: SkiGlance
    var body: some View {
        HStack(spacing: 5) {
            if g.onLift {
                Image(systemName: "cablecar.fill")
                Text("Lift").font(.subheadline.bold())
            } else {
                RunBar(color: g.runColor, width: 6, height: 16)
                Text("\(g.speedKmh)").font(SkiStyle.big(19)).monospacedDigit()
            }
        }
    }
}

/// Compact island, trailing side: km, or minutes to the top on a lift.
struct IslandCompactTrailing: View {
    let g: SkiGlance
    var body: some View {
        if g.onLift && g.liftMin > 0 {
            Text("top in \(g.liftMin) min").font(.subheadline.weight(.semibold)).foregroundStyle(SkiStyle.muted)
        } else {
            Text(String(format: "%.1f km", g.km)).font(SkiStyle.big(19)).monospacedDigit()
        }
    }
}

/// Apple Watch Smart Stack (iOS 18 / watchOS 11 show the phone's Live Activity on the wrist).
struct WatchStackGlance: View {
    let g: SkiGlance
    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline) {
                Text("\(g.speedKmh)").font(SkiStyle.big(40)).monospacedDigit()
                Text("km/h").font(.caption2.bold()).foregroundStyle(SkiStyle.muted)
                Spacer()
                Text(String(format: "%.1f km", g.km)).font(.headline).monospacedDigit()
            }
            HStack(spacing: 6) {
                if g.onLift {
                    Image(systemName: "cablecar.fill")
                    Text(g.liftName.isEmpty ? "On a lift" : g.liftName).font(.headline).lineLimit(1)
                } else {
                    RunBar(color: g.runColor, width: 6, height: 20)
                    Text(g.run.isEmpty ? "Free skiing" : g.run).font(.headline).lineLimit(1)
                }
            }
        }
        .foregroundStyle(.white)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(g.spoken)
    }
}
#endif
