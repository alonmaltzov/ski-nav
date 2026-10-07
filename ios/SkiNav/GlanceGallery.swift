import SwiftUI

/// QA only (`-qaGlances`): renders the real lock screen and Dynamic Island views with sample data,
/// so CI can screenshot them (a headless simulator can't show a locked screen).
struct GlanceGallery: View {
    private static func sample(lift: Bool) -> SkiGlance {
        let step = lift
            ? SkiGlance.Step(label: "Take Ardent gondola", color: "lift", ends: [[46.21378, 6.76099], [46.20792, 6.77813]],
                             nextLift: "Take Chaux Fleurie chair", nextLiftAt: [46.20701, 6.77827], then: "Ski Parchets (blue)", thenColor: "blue")
            : SkiGlance.Step(label: "Ski Chaux Fleuries (red) → Grand Plan (blue)", color: "red", ends: [[46.21169, 6.79035], [46.21378, 6.76099]],
                             nextLift: "Take Ardent gondola", nextLiftAt: [46.21378, 6.76099], then: "Take Ardent gondola", thenColor: "lift")
        var t = SkiTotals(); t.distM = 12_400; t.maxMps = 54 / 3.6; t.vertM = 1840
        return SkiGlance.make(speedMps: (lift ? 5 : 42) / 3.6, totals: t, onLift: lift,
                              at: lift ? [46.2100, 6.7710] : [46.2125, 6.7800], step: step)
    }

    var body: some View {
        let run = Self.sample(lift: false), lift = Self.sample(lift: true)
        ScrollView {
            VStack(spacing: 18) {
                caption("LOCK SCREEN")
                LockScreenGlance(g: run).background(card)
                LockScreenGlance(g: lift).background(card)
                caption("DYNAMIC ISLAND · COMPACT")
                pill { IslandCompactLeading(g: run) } trailing: { IslandCompactTrailing(g: run) }
                pill { IslandCompactLeading(g: lift) } trailing: { IslandCompactTrailing(g: lift) }
                caption("DYNAMIC ISLAND · EXPANDED")
                VStack(spacing: 10) { IslandExpandedTop(g: run); NowRow(g: run, nameSize: 22) }
                    .padding(20).foregroundStyle(.white)
                    .background(.black, in: RoundedRectangle(cornerRadius: 40, style: .continuous))
                caption("WATCH SMART STACK")
                WatchStackGlance(g: run).padding(12).frame(width: 190)
                    .background(Color(white: 0.15), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            }
            .padding(12)
        }
        .background(LinearGradient(colors: [Color(red: 0.30, green: 0.44, blue: 0.55), Color(red: 0.86, green: 0.90, blue: 0.93)],
                                   startPoint: .top, endPoint: .bottom).ignoresSafeArea())
        .onAppear { print("[app] QA SCREEN glances") }
    }

    private var card: some View { RoundedRectangle(cornerRadius: 24, style: .continuous).fill(Color(red: 0.03, green: 0.05, blue: 0.06).opacity(0.88)) }
    private func caption(_ s: String) -> some View {
        Text(s).font(.caption.weight(.bold)).foregroundStyle(.white.opacity(0.8)).frame(maxWidth: .infinity, alignment: .leading)
    }
    private func pill<L: View, T: View>(@ViewBuilder leading: () -> L, @ViewBuilder trailing: () -> T) -> some View {
        HStack { leading(); Spacer(); trailing() }
            .foregroundStyle(.white).padding(.horizontal, 16).frame(width: 260, height: 37)
            .background(.black, in: Capsule())
    }
}
