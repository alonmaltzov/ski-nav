#if os(iOS)
import SwiftUI

/// Lock screen Live Activity (v2): the next move first, speed on the right, the day underneath.
struct LockScreenGlance: View {
    let g: SkiGlance
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            NextMove(g: g, box: 52, title: 21)
            HStack {
                Text(String(format: "%.1f km · max %d", g.km, g.maxKmh)).font(.subheadline.weight(.semibold)).monospacedDigit()
                Spacer(minLength: 6)
                if !g.then.isEmpty && !g.onLift { Text("then \(g.then)").font(.subheadline.weight(.semibold)).lineLimit(1).minimumScaleFactor(0.8) }
            }
            .foregroundStyle(SkiStyle.muted)
        }
        .padding(.horizontal, 18).padding(.vertical, 14)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(g.spoken)
    }
}

/// The direction card: a coloured box (lift orange, or the run's colour), what's next and how far, speed on the right.
struct NextMove: View {
    let g: SkiGlance
    var box: CGFloat = 52
    var title: CGFloat = 21
    var eyebrow: String {
        if g.onLift { return g.liftMin > 0 ? "ON A LIFT · TOP IN \(g.liftMin) MIN" : "ON A LIFT" }
        if !g.nextLift.isEmpty { return g.nextLiftM >= 0 ? "NEXT · \(SkiText.km(Double(g.nextLiftM)).uppercased())" : "NEXT" }
        return g.run.isEmpty ? "SKIING" : "ON A \(SkiText.colorWord(g.runColor).uppercased())"
    }
    var name: String {
        if g.onLift { return g.liftName.isEmpty ? "On a lift" : g.liftName }
        if !g.nextLift.isEmpty { return g.nextLift }
        return g.run.isEmpty ? "Free skiing" : g.run
    }
    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                RoundedRectangle(cornerRadius: box * 0.3).fill(g.onLift || !g.nextLift.isEmpty ? SkiStyle.fill("orange") : SkiStyle.fill(g.runColor))
                Image(systemName: g.onLift || !g.nextLift.isEmpty ? "cablecar.fill" : "figure.skiing.downhill")
                    .font(.system(size: box * 0.46, weight: .bold)).foregroundStyle(.white)
            }
            .frame(width: box, height: box)
            VStack(alignment: .leading, spacing: 1) {
                Text(eyebrow).font(.caption2.weight(.heavy)).foregroundStyle(SkiStyle.muted).lineLimit(1)
                Text(name).font(SkiStyle.big(title)).foregroundStyle(.white).lineLimit(1).minimumScaleFactor(0.75)
            }
            Spacer(minLength: 4)
            VStack(alignment: .trailing, spacing: -2) {
                Text("\(g.speedKmh)").font(SkiStyle.big(box * 0.72)).monospacedDigit().foregroundStyle(g.onLift ? SkiStyle.muted : SkiStyle.accent)
                Text("KM/H").font(.caption2.weight(.heavy)).foregroundStyle(SkiStyle.muted)
            }
        }
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

/// Expanded Dynamic Island (v2): the same direction card.
struct IslandExpandedTop: View {
    let g: SkiGlance
    var body: some View { NextMove(g: g, box: 48, title: 20) }
}

/// Compact island, leading side: lift icon + metres to it (or minutes to the top), else the run colour + speed.
struct IslandCompactLeading: View {
    let g: SkiGlance
    var body: some View {
        HStack(spacing: 5) {
            if g.onLift {
                Image(systemName: "cablecar.fill").foregroundStyle(SkiStyle.accent)
                Text(g.liftMin > 0 ? "\(g.liftMin) min" : "Lift").font(.subheadline.bold()).monospacedDigit()
            } else if !g.nextLift.isEmpty && g.nextLiftM >= 0 {
                Image(systemName: "cablecar.fill").foregroundStyle(SkiStyle.accent)
                Text(SkiText.km(Double(g.nextLiftM))).font(.subheadline.bold()).monospacedDigit()
            } else {
                RunBar(color: g.runColor, width: 6, height: 16)
                Text(String(format: "%.1f km", g.km)).font(.subheadline.bold()).monospacedDigit()
            }
        }
    }
}

/// Compact island, trailing side: speed.
struct IslandCompactTrailing: View {
    let g: SkiGlance
    var body: some View {
        Text("\(g.speedKmh) km/h").font(SkiStyle.big(17)).monospacedDigit().foregroundStyle(g.onLift ? SkiStyle.muted : SkiStyle.accent)
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
