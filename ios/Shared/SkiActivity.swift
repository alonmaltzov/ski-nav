#if os(iOS)
import ActivityKit
import Foundation

/// What the lock screen and Dynamic Island show during a ski day.
struct SkiActivityAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var speedKmh: Int
        var km: Double
        var maxKmh: Int
        var vertM: Int
        var onLift: Bool
        var step: String        // "Ski Proclou (green)"
        var stepColor: String   // blue, red, black, green, lift, end
    }
    var dayTitle: String
    var startedAt: Date
}
#endif
