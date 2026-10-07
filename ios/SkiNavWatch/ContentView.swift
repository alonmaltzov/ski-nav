import SwiftUI
import WatchKit

/// Three vertical pages (Digital Crown or swipe): Now, today's steps, the ski-day controls.
/// "Now" switches between skiing and riding a lift by itself, from GPS speed and position. No taps needed.
struct ContentView: View {
    @EnvironmentObject var ski: SkiSession
    @State private var page = SkiSession.demoScreen == "steps" ? 1 : 0

    var body: some View {
        NavigationStack {
            TabView(selection: $page) {
                NowView().tag(0)
                StepsView().tag(1)
                ControlsView().tag(2)
            }
            .tabViewStyle(.verticalPage)
        }
    }
}

// MARK: - Now

struct NowView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        // re-read every few seconds so the phone's numbers are dropped once they go stale
        TimelineView(.periodic(from: .now, by: 5)) { _ in
            let g = ski.glance
            Group {
                if let g {
                    if g.onLift { LiftGlance(g: g) } else { RunGlance(g: g) }
                } else {
                    IdleView()
                }
            }
            .navigationTitle(g.map { String(format: "%.1f km", $0.km) } ?? "Ski Nav")
            .navigationBarTitleDisplayMode(.inline)
            .containerBackground(background(g).gradient, for: .tabView)
        }
    }
    private func background(_ g: SkiGlance?) -> Color {
        guard let g, !g.onLift else { return Color(white: 0.12) }
        return SkiStyle.fill(g.runColor).opacity(0.35)
    }
}

/// Skiing: big speed, the run you're on, the next lift.
struct RunGlance: View {
    let g: SkiGlance
    @Environment(\.isLuminanceReduced) private var dimmed
    @ScaledMetric(relativeTo: .largeTitle) private var speedSize: CGFloat = 72
    @ScaledMetric(relativeTo: .title3) private var nameSize: CGFloat = 22

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text("\(g.speedKmh)")
                    .font(SkiStyle.big(speedSize)).monospacedDigit()
                    .lineLimit(1).minimumScaleFactor(0.6)
                    .contentTransition(.numericText(value: Double(g.speedKmh)))
                Text("km/h").font(.headline).foregroundStyle(.secondary)
            }
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(g.speedKmh) kilometres per hour")

            if !g.run.isEmpty {
                VStack(alignment: .leading, spacing: 0) {
                    Text("ON · \(SkiText.colorWord(g.runColor).uppercased())")
                        .font(.caption2.weight(.bold)).foregroundStyle(.white.opacity(0.85))
                    Text(g.run).font(SkiStyle.big(nameSize)).lineLimit(2).minimumScaleFactor(0.75)
                }
                .padding(.horizontal, 10).padding(.vertical, 6)
                .frame(maxWidth: .infinity, alignment: .leading)
                .background(SkiStyle.fill(g.runColor).opacity(dimmed ? 0.45 : 1), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).strokeBorder(.white.opacity(g.runColor == "black" ? 0.6 : 0), lineWidth: 1.5))
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("On \(g.run), \(SkiText.colorWord(g.runColor)) run")
            }

            if !g.nextLift.isEmpty {
                HStack(spacing: 8) {
                    Image(systemName: "cablecar.fill").font(.title3).foregroundStyle(.secondary)
                    VStack(alignment: .leading, spacing: 0) {
                        Text(g.nextLift).font(.headline).lineLimit(1).minimumScaleFactor(0.8)
                        Text(g.nextLiftM >= 0 && g.nextLiftM < 20_000 ? "next lift · \(SkiText.km(Double(g.nextLiftM)))" : "next lift")
                            .font(.footnote).foregroundStyle(.secondary)
                    }
                }
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Next lift \(g.nextLift)" + (g.nextLiftM >= 0 && g.nextLiftM < 20_000 ? ", \(SkiText.km(Double(g.nextLiftM))) away" : ""))
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .opacity(dimmed ? 0.8 : 1)
    }
}

/// Riding a lift: which one, how far up, and the run after it. Distance is paused.
struct LiftGlance: View {
    let g: SkiGlance
    @Environment(\.isLuminanceReduced) private var dimmed
    @ScaledMetric(relativeTo: .title2) private var nameSize: CGFloat = 26
    @ScaledMetric(relativeTo: .title3) private var thenSize: CGFloat = 22

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Image(systemName: "cablecar.fill").font(.title3)
                VStack(alignment: .leading, spacing: 0) {
                    Text("ON LIFT · PAUSED").font(.caption2.weight(.bold)).foregroundStyle(.secondary)
                        .lineLimit(1).minimumScaleFactor(0.7)
                    Text(g.liftName.isEmpty ? "Lift" : g.liftName).font(SkiStyle.big(nameSize)).lineLimit(1).minimumScaleFactor(0.55)
                }
            }
            .accessibilityElement(children: .ignore)
            .accessibilityLabel(g.liftName.isEmpty ? "On a lift, distance paused" : "On \(g.liftName), distance paused")

            if !g.liftName.isEmpty {
                VStack(alignment: .leading, spacing: 4) {
                    ProgressView(value: g.liftProgress).tint(.white)
                    if g.liftMin > 0 {
                        Text("about \(g.liftMin) min to the top").font(.footnote).foregroundStyle(.secondary)
                    }
                }
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("\(Int(g.liftProgress * 100)) percent up" + (g.liftMin > 0 ? ", about \(g.liftMin) minutes to the top" : ""))
            }

            Spacer(minLength: 0)

            if !g.then.isEmpty {
                VStack(alignment: .leading, spacing: 2) {
                    Text("THEN").font(.caption2.weight(.bold)).foregroundStyle(.secondary)
                    HStack(spacing: 8) {
                        RunBar(color: g.thenColor, width: 7, height: 26)
                        Text(g.then).font(SkiStyle.big(thenSize)).lineLimit(1).minimumScaleFactor(0.7)
                    }
                }
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("Then \(g.then)")
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .opacity(dimmed ? 0.7 : 1)
    }
}

/// Nothing tracking yet.
struct IdleView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: "figure.skiing.downhill").font(.system(size: 36)).foregroundStyle(SkiStyle.accent)
                .accessibilityHidden(true)
            if let t = ski.plan?.title {
                Text(t).font(.headline).multilineTextAlignment(.center).lineLimit(2)
                Text("Start on your iPhone and this updates by itself.").font(.footnote).foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            } else {
                Text("Open Ski Nav on your iPhone to get today's plan.").font(.footnote).foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Steps

/// Today's plan as a list; scrolls itself to the step you're on.
struct StepsView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        Group {
            if let p = ski.plan {
                ScrollViewReader { proxy in
                    List(p.steps) { s in
                        StepRow(step: s, state: s.idx < ski.current ? .done : s.idx == ski.current ? .now : .later, nowNote: nowNote(s))
                            .id(s.idx)
                            .listRowBackground(RoundedRectangle(cornerRadius: 12, style: .continuous)
                                .fill(Color.white.opacity(s.idx == ski.current ? 0.2 : 0.07)))
                    }
                    .listStyle(.carousel)
                    .onAppear { proxy.scrollTo(ski.current, anchor: .center) }
                    .onChange(of: ski.current) { _, c in withAnimation { proxy.scrollTo(c, anchor: .center) } }
                }
            } else {
                VStack(spacing: 6) {
                    Image(systemName: "iphone").font(.title2).accessibilityHidden(true)
                    Text("Open Ski Nav on your iPhone to send today's plan.").font(.footnote).multilineTextAlignment(.center)
                }
            }
        }
        .navigationTitle("Today's plan")
        .navigationBarTitleDisplayMode(.inline)
        .containerBackground(SkiStyle.accent.opacity(0.3).gradient, for: .tabView)
    }
    private func nowNote(_ s: PlanStep) -> String {
        guard s.idx == ski.current else { return "" }
        if let g = ski.glance, g.onLift, g.liftMin > 0 { return "now · top in \(g.liftMin) min" }
        return s.at.isEmpty ? "now" : "now · planned \(s.at)"
    }
}

struct StepRow: View {
    enum Phase { case done, now, later }
    let step: PlanStep
    let state: Phase
    var nowNote = ""
    var body: some View {
        HStack(spacing: 10) {
            Text("\(step.idx + 1)")
                .font(.footnote.weight(.bold)).monospacedDigit().foregroundStyle(.white)
                .frame(width: 30, height: 30)
                .background(SkiStyle.fill(step.c), in: RoundedRectangle(cornerRadius: 8, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 8, style: .continuous).strokeBorder(.white.opacity(step.c == "black" ? 0.6 : 0), lineWidth: 1))
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: 4) {
                    if step.t == "lift" { Image(systemName: "cablecar.fill").font(.caption).foregroundStyle(.secondary) }
                    Text(SkiText.short(step.l)).font(state == .now ? .headline : .body).lineLimit(2)
                }
                if state == .now, !nowNote.isEmpty {
                    Text(nowNote).font(.caption2).foregroundStyle(.secondary)
                }
            }
        }
        .padding(.vertical, 4)
        .opacity(state == .done ? 0.45 : 1)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Step \(step.idx + 1), \(step.t == "lift" ? "lift" : SkiText.colorWord(step.c) + " run"), \(SkiText.short(step.l))"
                            + (state == .now ? ", current step" : state == .done ? ", done" : ""))
    }
}

// MARK: - Controls

struct ControlsView: View {
    @EnvironmentObject var ski: SkiSession
    @State private var confirmEnd = false
    var body: some View {
        ScrollView {
            VStack(spacing: 10) {
                if let g = ski.glance {
                    Grid(horizontalSpacing: 12, verticalSpacing: 6) {
                        GridRow {
                            stat("\(g.maxKmh)", "max km/h")
                            stat(g.vertM.formatted(), "vert m")
                        }
                        if ski.running {
                            GridRow {
                                stat(time(ski.elapsed), "time")
                                stat(ski.gpsOK ? "Good" : "Weak", "GPS")
                            }
                        }
                    }
                }
                if ski.fromPhone && ski.phoneTracking {
                    Label("Showing your iPhone's tracking", systemImage: "iphone")
                        .font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)
                }
                if ski.running {
                    Button(role: .destructive) { confirmEnd = true } label: {
                        Label("End ski day", systemImage: "stop.fill").frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent).tint(.red)
                } else {
                    Button { ski.start() } label: {
                        Label("Track on watch", systemImage: "play.fill").frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent).tint(SkiStyle.accent)
                    Text("Use this when your iPhone stays at the hotel. Saved as a Downhill Skiing workout.")
                        .font(.caption2).foregroundStyle(.secondary).multilineTextAlignment(.center)
                }
                if let m = ski.message {
                    Text(m).font(.caption2).foregroundStyle(.orange).multilineTextAlignment(.center)
                }
            }
        }
        .navigationTitle(ski.plan.map { "Day \($0.day)" } ?? "Ski day")
        .navigationBarTitleDisplayMode(.inline)
        .confirmationDialog("End today's ski day?", isPresented: $confirmEnd) {
            Button("End ski day", role: .destructive) { ski.stop() }
            Button("Keep tracking", role: .cancel) {}
        }
    }

    private func stat(_ v: String, _ l: String) -> some View {
        VStack(spacing: 0) {
            Text(v).font(SkiStyle.big(26)).monospacedDigit()
            Text(l).font(.caption2).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .accessibilityElement(children: .combine)
    }
    private func time(_ t: TimeInterval) -> String {
        let m = Int(t) / 60
        return String(format: "%d:%02d", m / 60, m % 60)
    }
}
