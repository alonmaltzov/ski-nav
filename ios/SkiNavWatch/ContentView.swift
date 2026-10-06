import SwiftUI
import WatchKit

private func color(_ c: String) -> Color {
    switch c {
    case "blue": return Color(red: 0.11, green: 0.37, blue: 0.88)
    case "red": return Color(red: 0.85, green: 0.12, blue: 0.15)
    case "black": return .black
    case "green": return Color(red: 0.09, green: 0.64, blue: 0.29)
    case "end": return Color(red: 1.0, green: 0.35, blue: 0.12)
    default: return Color(white: 0.35)   // lift
    }
}

struct ContentView: View {
    @EnvironmentObject var ski: SkiSession

    var body: some View {
        TabView {
            NowView()
            StatsView()
            StepView()
            ControlsView()
        }
        .tabViewStyle(.verticalPage)
    }
}

/// Page 1: one glance - speed, what you're on now, the next lift. Uses the watch's own tracking when it runs,
/// otherwise the iPhone's live numbers (sent while the phone tracks and this app is open).
struct NowView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        let live = ski.phone.flatMap { Date().timeIntervalSince($0.at) < 20 ? $0 : nil }
        let speed = ski.running ? ski.speedKmh : (live?.speedKmh ?? 0)
        let km = ski.running ? ski.distanceKm : (live?.km ?? 0)
        let lift = ski.running ? ski.onLift : (live?.onLift ?? false)
        let nowLabel = live?.step ?? ski.step?.l
        let nowColor = live?.color ?? ski.step?.c ?? "lift"
        let next = (live?.next).flatMap { $0.isEmpty ? nil : $0 } ?? ski.nextLift?.l
        VStack(alignment: .leading, spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text("\(Int(speed.rounded()))").font(.system(size: 48, weight: .bold, design: .rounded)).monospacedDigit()
                    .foregroundStyle(lift ? .secondary : .primary)
                Text(lift ? "LIFT" : "km/h").font(.caption2.bold()).foregroundStyle(.secondary)
                Spacer()
                Text(String(format: "%.1f km", km)).font(.caption.monospacedDigit()).foregroundStyle(.secondary)
            }
            if let n = nowLabel {
                HStack(alignment: .top, spacing: 6) {
                    RoundedRectangle(cornerRadius: 3).fill(color(nowColor)).frame(width: 6)
                    Text(n).font(.headline).lineLimit(2).minimumScaleFactor(0.75)
                }.fixedSize(horizontal: false, vertical: true)
            }
            if let nx = next {
                Label(nx, systemImage: "cablecar").font(.caption).foregroundStyle(.secondary).lineLimit(2)
            }
            if !ski.running && live == nil {
                Text(ski.plan == nil ? "Open Ski Nav on your iPhone" : "Start on the iPhone, or swipe up to start here")
                    .font(.caption2).foregroundStyle(.secondary)
            } else if !ski.running, live != nil {
                Text("from iPhone").font(.caption2).foregroundStyle(.secondary)
            }
        }
        .padding(.horizontal, 4)
    }
}

/// Page 2: the numbers.
struct StatsView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text("\(Int(ski.speedKmh.rounded()))")
                    .font(.system(size: 54, weight: .bold, design: .rounded))
                    .foregroundStyle(ski.onLift ? .secondary : .primary)
                    .monospacedDigit()
                Text("km/h").font(.footnote).foregroundStyle(.secondary)
                Spacer()
                if ski.onLift { Text("LIFT").font(.caption2.bold()).padding(.horizontal, 5).padding(.vertical, 2).background(.gray.opacity(0.35), in: Capsule()) }
            }
            Grid(alignment: .leading, horizontalSpacing: 10, verticalSpacing: 2) {
                GridRow {
                    stat(String(format: "%.1f", ski.distanceKm), "km")
                    stat("\(Int(ski.maxKmh.rounded()))", "max")
                }
                GridRow {
                    stat("\(Int(ski.verticalM.rounded()))", "vert m")
                    stat(time(ski.elapsed), "time")
                }
            }
            if !ski.running {
                Text("Swipe up to start").font(.caption2).foregroundStyle(.secondary).padding(.top, 2)
            } else if !ski.gpsOK {
                Text("Finding GPS…").font(.caption2).foregroundStyle(.orange).padding(.top, 2)
            }
        }
        .padding(.horizontal, 4)
    }
    private func stat(_ v: String, _ l: String) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text(v).font(.system(.title3, design: .rounded).bold()).monospacedDigit()
            Text(l).font(.caption2).foregroundStyle(.secondary)
        }
    }
    private func time(_ t: TimeInterval) -> String {
        let m = Int(t) / 60
        return String(format: "%d:%02d", m / 60, m % 60)
    }
}

/// Page 2: what to do now, and what's next.
struct StepView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        if let s = ski.step, let p = ski.plan {
            VStack(alignment: .leading, spacing: 6) {
                Text("STEP \(ski.current + 1) OF \(p.steps.count)\(s.at.isEmpty ? "" : " · \(s.at)")")
                    .font(.caption2).foregroundStyle(.secondary)
                HStack(alignment: .top, spacing: 8) {
                    RoundedRectangle(cornerRadius: 4).fill(color(s.c)).frame(width: 8)
                    Text(s.l).font(.headline).lineLimit(3).minimumScaleFactor(0.8)
                }
                .fixedSize(horizontal: false, vertical: true)
                if let n = ski.nextStep {
                    Text("Then: \(n.l)").font(.caption).foregroundStyle(.secondary).lineLimit(2)
                }
                HStack {
                    Button { ski.previousManually() } label: { Image(systemName: "chevron.left") }
                    Button { ski.nextManually() } label: { Image(systemName: "chevron.right") }
                }
            }
        } else {
            VStack(spacing: 6) {
                Image(systemName: "iphone.and.arrow.forward").font(.title2)
                Text("Open Ski Nav on your iPhone to send today's plan.").font(.footnote).multilineTextAlignment(.center)
            }
        }
    }
}

/// Page 3: start / stop.
struct ControlsView: View {
    @EnvironmentObject var ski: SkiSession
    var body: some View {
        VStack(spacing: 8) {
            if let t = ski.plan?.title { Text(t).font(.caption).foregroundStyle(.secondary).lineLimit(2).multilineTextAlignment(.center) }
            Button(ski.running ? "End ski day" : "Start ski day") {
                ski.running ? ski.stop() : ski.start()
            }
            .tint(ski.running ? .red : .blue)
            if let m = ski.message { Text(m).font(.caption2).foregroundStyle(.orange).multilineTextAlignment(.center) }
        }
    }
}
