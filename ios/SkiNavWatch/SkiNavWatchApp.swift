import SwiftUI
import WatchKit
import HealthKit

@main
struct SkiNavWatchApp: App {
    @WKApplicationDelegateAdaptor(WatchDelegate.self) private var delegate
    @StateObject private var ski = SkiSession.shared

    var body: some Scene {
        WindowGroup {
            ContentView().environmentObject(ski)
        }
    }
}

/// The iPhone's Start button launches this app with a workout configuration: start the ski day on the wrist.
final class WatchDelegate: NSObject, WKApplicationDelegate {
    func handle(_ workoutConfiguration: HKWorkoutConfiguration) {
        print("[watch] started from the iPhone")
        Task { @MainActor in SkiSession.shared.startFromPhone() }
    }
}
