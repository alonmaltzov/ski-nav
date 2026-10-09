import SwiftUI
import WidgetKit

/// The complication's four sizes, drawn from SkiFace.Content (same views on the watch face and in the QA demo).
struct FaceRing: View {
    let c: SkiFace.Content
    var body: some View {
        ZStack {
            AccessoryWidgetBackground()
            Circle().stroke(Color.white.opacity(0.18), lineWidth: 4.5).padding(3)
            Circle().trim(from: 0, to: max(0.001, min(1, c.ring)))
                .stroke(SkiStyle.accent, style: StrokeStyle(lineWidth: 4.5, lineCap: .round))
                .rotationEffect(.degrees(-90)).padding(3)
                .widgetAccentable()
            if c.ringCheck {
                Image(systemName: "checkmark").font(.system(size: 20, weight: .bold)).foregroundStyle(SkiStyle.accent).widgetAccentable()
            } else {
                VStack(spacing: -1) {
                    Text(c.ringCenter).font(SkiStyle.big(19)).minimumScaleFactor(0.6).lineLimit(1)
                    if !c.ringUnit.isEmpty { Text(c.ringUnit).font(.system(size: 7.5, weight: .bold)).foregroundStyle(.secondary).lineLimit(1) }
                }
                .padding(.horizontal, 7)
            }
        }
        .accessibilityLabel(c.inline)
    }
}

struct FaceRect: View {
    let c: SkiFace.Content
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Text(c.top).font(.system(size: 11, weight: .bold)).foregroundStyle(SkiStyle.accent).widgetAccentable().lineLimit(1)
                Spacer(minLength: 4)
                Text(c.topRight).font(.system(size: 11, weight: .semibold)).foregroundStyle(.secondary).lineLimit(1)
            }
            HStack(spacing: 5) {
                if !c.titleColor.isEmpty { RunBar(color: c.titleColor, width: 5, height: 16) }
                Text(c.title).font(SkiStyle.big(18)).lineLimit(1).minimumScaleFactor(0.75)
            }
            if let b = c.bar {
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule().fill(Color.white.opacity(0.18))
                        Capsule().fill(c.barWhite ? Color.white : SkiStyle.accent).frame(width: max(4, geo.size.width * min(1, b))).widgetAccentable()
                    }
                }
                .frame(height: 4)
            }
            if !c.sub1.isEmpty { Text(c.sub1).font(.system(size: 12, weight: .medium)).foregroundStyle(.secondary).lineLimit(1).minimumScaleFactor(0.8) }
            if !c.sub2.isEmpty && c.bar == nil { Text(c.sub2).font(.system(size: 12, weight: .medium)).foregroundStyle(.secondary).lineLimit(1).minimumScaleFactor(0.8) }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .accessibilityElement(children: .combine)
    }
}

struct FaceCorner: View {
    let c: SkiFace.Content
    var body: some View {
        Image(systemName: c.mode == .lift ? "cablecar" : c.mode == .done ? "checkmark" : "figure.skiing.downhill")
            .font(.title3.weight(.semibold))
            .widgetLabel { Text(c.corner) }
            .accessibilityLabel(c.inline)
    }
}

struct FaceInline: View {
    let c: SkiFace.Content
    var body: some View {
        Label(c.inline, systemImage: c.mode == .lift ? "cablecar" : "figure.skiing.downhill")
    }
}
