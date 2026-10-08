import SwiftUI

@main
struct SkiNavApp: App {
    @StateObject private var location = LocationService.shared
    @Environment(\.scenePhase) private var phase

    init() {
        WatchLink.shared.activate()
        if !LocationService.shared.isTracking { SkiDay.endAll() }
    }

    var body: some Scene {
        WindowGroup {
            if ProcessInfo.processInfo.arguments.contains("-qaGlances") {
                GlanceGallery()
            } else {
                app
            }
        }
    }

    private var app: some View {
            WebAppView()
                .ignoresSafeArea()
                .onOpenURL { WebBridge.shared.openJoin($0) }
                .onChange(of: phase) { _, newPhase in
                    // when we come back to the foreground, hand the web app everything recorded while locked
                    if newPhase == .active { WebBridge.shared.flush(); WebUpdater.checkForUpdate() }
                }
    }
}
