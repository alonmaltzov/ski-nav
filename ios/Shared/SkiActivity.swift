#if os(iOS)
import ActivityKit
import Foundation

/// What the lock screen, the Dynamic Island and the watch Smart Stack show during a ski day.
struct SkiActivityAttributes: ActivityAttributes {
    typealias ContentState = SkiGlance
    var dayTitle: String
    var startedAt: Date
}
#endif
