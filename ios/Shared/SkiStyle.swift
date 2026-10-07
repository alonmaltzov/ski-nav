import SwiftUI

/// Colours and type shared by every Ski Nav surface (phone widgets, watch).
enum SkiStyle {
    static func fill(_ c: String) -> Color {
        switch c {
        case "blue": return Color(red: 0.11, green: 0.37, blue: 0.88)
        case "red": return Color(red: 0.85, green: 0.12, blue: 0.15)
        case "black": return Color(white: 0.08)
        case "green": return Color(red: 0.08, green: 0.50, blue: 0.24)
        case "orange": return Color(red: 0.98, green: 0.45, blue: 0.09)
        case "end": return Color(red: 1.0, green: 0.54, blue: 0.24)
        default: return Color(red: 0.28, green: 0.33, blue: 0.41)   // lift
        }
    }
    /// Ski Nav's accent (the orange from the mockups).
    static let accent = Color(red: 1.0, green: 0.54, blue: 0.24)
    static let muted = Color(red: 0.60, green: 0.65, blue: 0.70)

    /// Big numbers: system font, condensed, bold (SF Pro Condensed).
    static func big(_ size: CGFloat) -> Font { .system(size: size, weight: .bold).width(.condensed) }
}

/// The colour chip for a run; black runs get a light outline so they show on a dark background.
struct RunBar: View {
    let color: String
    var width: CGFloat = 8
    var height: CGFloat = 28
    var body: some View {
        RoundedRectangle(cornerRadius: width / 2)
            .fill(SkiStyle.fill(color))
            .overlay(RoundedRectangle(cornerRadius: width / 2).strokeBorder(.white.opacity(color == "black" ? 0.7 : 0), lineWidth: 1.5))
            .frame(width: width, height: height)
            .accessibilityHidden(true)
    }
}

extension SkiGlance {
    /// Spoken summary for VoiceOver.
    var spoken: String {
        var parts = ["\(speedKmh) kilometres per hour", String(format: "%.1f kilometres today", km)]
        if onLift {
            parts.append(liftName.isEmpty ? "on a lift" : "on \(liftName)")
            if liftMin > 0 { parts.append("about \(liftMin) minutes to the top") }
        } else if !run.isEmpty {
            parts.append("on \(run), \(SkiText.colorWord(runColor))")
        }
        if !upNext.isEmpty { parts.append("then \(upNext)") }
        return parts.joined(separator: ", ")
    }
}
