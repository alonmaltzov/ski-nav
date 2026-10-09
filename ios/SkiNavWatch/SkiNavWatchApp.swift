import SwiftUI
import WatchKit
import HealthKit

@main
struct SkiNavWatchApp: App {
    @WKApplicationDelegateAdaptor(WatchDelegate.self) private var delegate
    @StateObject private var ski = SkiSession.shared

    var body: some Scene {
        WindowGroup {
            if let d = SkiSession.demoScreen, d.hasPrefix("face-") {
                FaceDemo(mode: String(d.dropFirst(5)))
            } else {
                ContentView().environmentObject(ski)
            }
        }
    }
}

/// The iPhone's Start button launches this app with a workout configuration: start the ski day on the wrist.
final class WatchDelegate: NSObject, WKApplicationDelegate {
    /// launched in the background (a complication update from the phone): start the phone link
    func applicationDidFinishLaunching() { Task { @MainActor in _ = SkiSession.shared } }

    func handle(_ workoutConfiguration: HKWorkoutConfiguration) {
        print("[watch] started from the iPhone")
        Task { @MainActor in SkiSession.shared.startFromPhone() }
    }
}

/// QA only (`-demo face-skiing` etc.): a watch face with the Ski Nav complications in one state, sample data.
struct FaceDemo: View {
    let mode: String
    private var sample: (SkiFace, Date) {
        var f = SkiFace()
        let day3 = Calendar.current.date(byAdding: .day, value: 2, to: SkiFace.tripStart)!
        var at = Calendar.current.date(bySettingHour: 10, minute: 42, second: 0, of: day3)!
        f.dayKey = SkiFace.key(day3); f.day = 3; f.title = "Châtel side: Pré-la-Joux"; f.kmPlan = 24; f.firstAt = "9:15"; f.firstLift = "Proclou chair"
        var g = SkiGlance(); g.km = 12.4; g.maxKmh = 61; g.vertM = 3400
        switch mode {
        case "morning": at = Calendar.current.date(bySettingHour: 8, minute: 42, second: 0, of: day3)!; g = SkiGlance()
        case "lift": g.onLift = true; g.liftName = "Ardent gondola"; g.liftProgress = 0.6; g.liftMin = 4; g.then = "Lindarets"; g.thenColor = "blue"; f.tracking = true
            at = Calendar.current.date(bySettingHour: 11, minute: 5, second: 0, of: day3)!
        case "done": g.km = 26.1; at = Calendar.current.date(bySettingHour: 15, minute: 20, second: 0, of: day3)!
        default: g.speedKmh = 42; g.run = "Chaux Fleuries"; g.runColor = "red"; g.nextLift = "Ardent gondola"; g.nextLiftM = 1200; f.tracking = true
        }
        f.g = g; f.updated = at
        return (f, at)
    }
    var body: some View {
        let (f, at) = sample
        let c = f.content(at: at)
        VStack(alignment: .leading, spacing: 6) {
            FaceInline(c: c).font(.system(size: 12, weight: .semibold)).foregroundStyle(SkiStyle.accent).lineLimit(1)
            HStack {
                FaceRing(c: c).frame(width: 50, height: 50)
                Spacer()
                Text(at, format: .dateTime.hour().minute()).font(SkiStyle.big(34)).lineLimit(1).minimumScaleFactor(0.6)
            }
            FaceRect(c: c).padding(8).background(Color(white: 0.12), in: RoundedRectangle(cornerRadius: 12))
        }
        .padding(.horizontal, 6)
        .onAppear { print("[watch] QA SCREEN face-\(mode): \(c.inline)") }
    }
}
