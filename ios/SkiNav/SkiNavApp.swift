import SwiftUI
import UserNotifications

@main
struct SkiNavApp: App {
    @StateObject private var location = LocationService.shared
    @Environment(\.scenePhase) private var phase

    init() {
        WatchLink.shared.activate()
        UNUserNotificationCenter.current().delegate = Guide.shared   // the morning brief notification opens the brief
        if !LocationService.shared.isTracking { SkiDay.endAll() }
    }

    var body: some Scene {
        WindowGroup {
            if ProcessInfo.processInfo.arguments.contains("-qaGlances") {
                GlanceGallery()
            } else if ProcessInfo.processInfo.arguments.contains("-glassDemo"), let demo = glassDemo {
                demo
            } else {
                app
            }
        }
    }

    /// Liquid Glass demo (demo branch): native glass controls over the unchanged web map
    private var glassDemo: AnyView? {
        #if compiler(>=6.2)
        if #available(iOS 26.0, *) { return AnyView(GlassDemoRoot()) }
        #endif
        return nil
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
