import SwiftUI

@main
struct SkiNavWatchApp: App {
    @StateObject private var ski = SkiSession()

    var body: some Scene {
        WindowGroup {
            ContentView().environmentObject(ski)
        }
    }
}
