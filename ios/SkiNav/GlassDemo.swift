import SwiftUI
import WebKit

// Liquid Glass demo (demo branch only). Launched with -glassDemo, the app keeps the web map exactly as it is
// and draws the controls on top with Apple's own glass (iOS 26 SDK): a native tab bar, glass map buttons,
// a glass card and a glass sheet. -glassDemoAuto plays a scripted walk-through for the screen recording.

#if compiler(>=6.2)
@available(iOS 26.0, *)
struct GlassDemoRoot: View {
    @State private var tab = 0
    @State private var showRoute = false
    @State private var detent: PresentationDetent = .medium
    @State private var title = "Avoriaz"
    @State private var eyebrow = "SUN JAN 17 · TODAY"
    @State private var meta = "57.2 km of runs · 24 lifts · Folie Douce 16:45"

    var body: some View {
        TabView(selection: $tab) {
            Tab("Today", systemImage: "mountain.2.fill", value: 0) { today }
            Tab("Week", systemImage: "calendar", value: 1) { DemoWeek() }
            Tab("Crew", systemImage: "person.2.fill", value: 2) { DemoCrew() }
            Tab("Games", systemImage: "trophy.fill", value: 3) { DemoGames() }
            Tab("Ask Shai", systemImage: "bubble.left.and.text.bubble.right.fill", value: 4, role: .search) { DemoAsk() }
        }
        .tint(.blue)
        .sheet(isPresented: $showRoute) {
            DemoRoute()
                .presentationDetents([.medium, .large], selection: $detent)
                .presentationBackgroundInteraction(.enabled(upThrough: .medium))
        }
        .task { await readHome() }
        .task { if ProcessInfo.processInfo.arguments.contains("-glassDemoAuto") { await autoplay() } }
    }

    // MARK: Today: the unchanged web map, glass controls on top
    private var today: some View {
        ZStack {
            WebAppView().ignoresSafeArea()
            VStack(spacing: 0) {
                HStack(alignment: .top) {
                    GlassEffectContainer(spacing: 10) {
                        HStack(spacing: 10) {
                            Button { web("$('wxPill').click()") } label: {
                                HStack(spacing: 8) {
                                    ShaiFace().frame(width: 30, height: 30)
                                    VStack(alignment: .leading, spacing: 0) {
                                        Text("Shai").font(.subheadline.weight(.semibold))
                                        Text("Today's brief").font(.caption2).foregroundStyle(.secondary)
                                    }
                                }.padding(.trailing, 6)
                            }
                            .buttonStyle(.glass)
                            Button { web("$('liftsPill').click()") } label: {
                                Label("Lifts open", systemImage: "cablecar.fill").font(.subheadline.weight(.semibold))
                            }
                            .buttonStyle(.glass)
                        }
                    }
                    Spacer()
                    GlassEffectContainer(spacing: 0) {
                        VStack(spacing: 0) {
                            mapButton("location.fill", "followBtn", "Follow me")
                            mapButton("location.north.line", "compassBtn", "Compass")
                            mapButton("arrow.up.left.and.arrow.down.right", "fitBtn", "Whole route")
                            mapButton("view.3d", "dimBtn", "2D or 3D")
                            mapButton("fork.knife", "placesBtn", "Places")
                            mapButton("crown.fill", "kingBtn", "Speed King", tint: .yellow)
                        }
                        .glassEffect(.regular.interactive(), in: .capsule)
                    }
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
                Spacer()
                todayCard
                    .padding(.horizontal, 12)
                    .padding(.bottom, 8)
            }
        }
    }

    private func mapButton(_ symbol: String, _ id: String, _ label: String, tint: Color = .primary) -> some View {
        Button { web("$('\(id)').click()") } label: {
            Image(systemName: symbol).font(.system(size: 17, weight: .semibold)).foregroundStyle(tint)
                .frame(width: 48, height: 46)
        }
        .accessibilityLabel(label)
    }

    private var todayCard: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(eyebrow).font(.caption.weight(.semibold)).foregroundStyle(.secondary)
            Text(title).font(.largeTitle.bold())
            Text(meta).font(.subheadline).foregroundStyle(.secondary)
            HStack(spacing: 10) {
                Button { web("$('goBtn').click()") } label: {
                    Label("Start Skiing", systemImage: "play.fill").font(.headline).frame(maxWidth: .infinity).padding(.vertical, 6)
                }
                .buttonStyle(.glassProminent)
                Button { detent = .medium; showRoute = true } label: {
                    Text("Route").font(.headline).padding(.horizontal, 10).padding(.vertical, 6)
                }
                .buttonStyle(.glass)
            }
            .padding(.top, 10)
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassEffect(.regular, in: .rect(cornerRadius: 32))
    }

    private func web(_ js: String) {
        WebBridge.shared.js("(function(){ const $=id=>document.getElementById(id); \(js) })()")
    }

    /// today's title and numbers come from the web app, so the card always matches the map
    private func readHome() async {
        for _ in 0..<40 {
            try? await Task.sleep(for: .milliseconds(500))
            guard WebBridge.shared.pageReady, let w = WebBridge.shared.webView else { continue }
            let js = "JSON.stringify([document.getElementById('homeEyebrow').textContent, document.getElementById('homeTitle').textContent, document.getElementById('homeMeta').textContent])"
            if let s = try? await w.evaluateJavaScript(js) as? String,
               let d = s.data(using: .utf8), let a = try? JSONDecoder().decode([String].self, from: d), a.count == 3, !a[1].isEmpty {
                eyebrow = a[0].uppercased(); title = a[1]; meta = a[2]
                return
            }
        }
    }

    /// the scripted walk-through for the screen recording: tabs, then the route sheet, then Ask
    private func autoplay() async {
        func wait(_ s: Double) async { try? await Task.sleep(for: .seconds(s)) }
        await wait(48)   // the simulator draws the 3D map slowly; start once it's on screen
        print("[demo] home"); await wait(3)
        print("[demo] tab week");   withAnimation { tab = 1 }; await wait(2.5)
        print("[demo] tab crew");   withAnimation { tab = 2 }; await wait(2.5)
        print("[demo] tab games");  withAnimation { tab = 3 }; await wait(2.5)
        print("[demo] tab today");  withAnimation { tab = 0 }; await wait(2.5)
        print("[demo] route sheet"); detent = .medium; showRoute = true; await wait(3)
        print("[demo] sheet large"); withAnimation { detent = .large }; await wait(3)
        print("[demo] sheet close"); showRoute = false; await wait(2.5)
        print("[demo] ask");        withAnimation { tab = 4 }; await wait(3)
        print("[demo] back today"); withAnimation { tab = 0 }; await wait(2)
        print("[demo] DONE")
    }
}

@available(iOS 26.0, *)
private struct ShaiFace: View {
    var body: some View {
        ZStack {
            Circle().fill(Color(red: 1, green: 0.96, blue: 0.92))
            Image(systemName: "face.smiling.inverse").resizable().scaledToFit().padding(5).foregroundStyle(Color(red: 0.24, green: 0.16, blue: 0.13))
        }
        .clipShape(Circle())
    }
}

// MARK: Demo content for the other tabs (native lists, same data as the mockups)
@available(iOS 26.0, *)
private struct DemoWeek: View {
    let days: [(String, String, String, Bool)] = [("Sun 17", "Avoriaz", "57 km · 24 lifts", false),
        ("Mon 18", "Morzine + Les Gets", "54 km", false), ("Tue 19", "Les Crosets", "51 km", true),
        ("Wed 20", "Champoussin", "59 km", true), ("Thu 21", "Châtel + Linga", "53 km", false),
        ("Fri 22", "Super-Châtel", "52 km", true)]
    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 14) {
                        ZStack {
                            Circle().stroke(.red.opacity(0.18), lineWidth: 9)
                            Circle().trim(from: 0, to: 0.07).stroke(.red, style: StrokeStyle(lineWidth: 9, lineCap: .round)).rotationEffect(.degrees(-90))
                        }.frame(width: 52, height: 52)
                        VStack(alignment: .leading) {
                            Text("WEEK GOAL").font(.caption.weight(.semibold)).foregroundStyle(.red)
                            Text("7 of 100 reds").font(.title3.bold())
                            Text("68 in this week's plan").font(.subheadline).foregroundStyle(.secondary)
                        }
                    }.padding(.vertical, 4)
                }
                Section("Plan") {
                    ForEach(days, id: \.0) { d in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(d.1).font(.headline)
                                Text("\(d.0) · \(d.2)").font(.subheadline).foregroundStyle(.secondary)
                            }
                            Spacer()
                            if d.3 { Label("Passport", systemImage: "cross.fill").font(.caption.weight(.semibold)).foregroundStyle(.red) }
                        }
                    }
                }
            }
            .navigationTitle("Avoriaz Week")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) { Button("Invite", systemImage: "square.and.arrow.up") {} }
                ToolbarItem(placement: .topBarTrailing) { Button("Settings", systemImage: "gearshape") {} }
            }
        }
    }
}

@available(iOS 26.0, *)
private struct DemoCrew: View {
    let crew: [(String, Color, String, String)] = [("Avsha", .purple, "On Les Tannes · 1 min ago", "1.2 km"),
        ("Kelner", .green, "On Prolays chair · now", "800 m"), ("Yuval", .red, "At Le Pas du Lac · 4 min ago", "2.3 km")]
    var body: some View {
        NavigationStack {
            List {
                Section {
                    ForEach(crew, id: \.0) { m in
                        HStack(spacing: 12) {
                            Circle().fill(m.1).frame(width: 40, height: 40).overlay(Text(String(m.0.prefix(1))).font(.headline).foregroundStyle(.white))
                            VStack(alignment: .leading) { Text(m.0).font(.headline); Text(m.2).font(.subheadline).foregroundStyle(.secondary) }
                            Spacer()
                            Button(m.3) {}.buttonStyle(.glass)
                        }
                    }
                }
                Section {
                    Label("Set a Meet Point", systemImage: "mappin.and.ellipse")
                    Label("Talk with the Group", systemImage: "phone.fill")
                    Label("Split Costs", systemImage: "creditcard.fill")
                }
            }
            .navigationTitle("Crew")
            .toolbar { ToolbarItem(placement: .topBarTrailing) { Button("Invite", systemImage: "person.badge.plus") {} } }
        }
    }
}

@available(iOS 26.0, *)
private struct DemoGames: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Today's rounds") {
                    Label("STOPPP 1 · 11:00 to 12:20 · Avsha", systemImage: "1.circle.fill")
                    Label("STOPPP 2 · 12:20 to 13:40 · Kelner", systemImage: "2.circle.fill")
                    Label("STOPPP 3 · 13:40 to 15:00 · Yuval", systemImage: "3.circle.fill")
                }
                Section { Label("Fastest today: Yuval, 71 km/h", systemImage: "crown.fill") }
                Section {
                    Toggle("STOPPP", isOn: .constant(true))
                    Toggle("Count Me In for Rounds", isOn: .constant(true))
                    Toggle("Passport Race", isOn: .constant(true))
                    Toggle("Speed King", isOn: .constant(true))
                    Toggle("Crew Voice Clips", isOn: .constant(true))
                }
            }
            .navigationTitle("Games")
        }
    }
}

@available(iOS 26.0, *)
private struct DemoAsk: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Try") {
                    ForEach(["What's next?", "Where's lunch?", "Any lifts closed?", "Plan from here", "How much today?", "Call the group"], id: \.self) { Text($0) }
                }
            }
            .navigationTitle("Ask Shai")
            .searchable(text: .constant(""), prompt: "Ask anything about today")
        }
    }
}

@available(iOS 26.0, *)
private struct DemoRoute: View {
    let steps: [(String, String, String, Color)] = [("Proclou", "Chairlift · every morning", "9:00", .gray),
        ("Combe à Floret", "Blue · 770 m", "9:15", .blue), ("Les Tannes", "Red · 1.2 km", "9:18", .red),
        ("Prolays", "Chairlift", "9:24", .gray), ("Crête to Jean Vuarnet", "Blue then red · 3 km", "9:32", .red),
        ("Grandes Combes", "Chairlift · 1.8 km", "9:44", .gray), ("Jean Vuarnet", "Red · 900 m", "9:53", .red)]
    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack {
                        Button("Plan from Here", systemImage: "location.fill") {}.buttonStyle(.glassProminent)
                        Button("Original Plan") {}.buttonStyle(.glass)
                    }
                }
                ForEach(Array(steps.enumerated()), id: \.offset) { i, s in
                    HStack(spacing: 12) {
                        Text("\(i + 1)").font(.subheadline.bold()).foregroundStyle(.white)
                            .frame(width: 30, height: 30).background(s.3, in: .rect(cornerRadius: 9))
                        VStack(alignment: .leading) { Text(s.0).font(.headline); Text(s.1).font(.subheadline).foregroundStyle(.secondary) }
                        Spacer()
                        Text(s.2).monospacedDigit().foregroundStyle(.secondary)
                    }
                }
            }
            .navigationTitle("Route")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}
#endif
