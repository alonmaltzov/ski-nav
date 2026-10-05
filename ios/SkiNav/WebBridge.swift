import SwiftUI
import WebKit

/// Connects the web app (index.html) to native code.
/// JS -> native: window.webkit.messageHandlers.skinav.postMessage({cmd: ...})
/// native -> JS: window.__native.fixes([...]) and window.__native.event(name)
final class WebBridge: NSObject, WKScriptMessageHandler {
    static let shared = WebBridge()
    weak var webView: WKWebView?
    private var pageReady = false

    func userContentController(_ c: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let cmd = body["cmd"] as? String else { return }
        switch cmd {
        case "ready":
            pageReady = true
            flush()
        case "start":
            LocationService.shared.start()
        case "stop":
            LocationService.shared.stop()
        case "plan":
            // today's steps, forwarded to the watch so it can show "next step" on the wrist
            WatchLink.shared.sendPlan(body)
        default:
            break
        }
    }

    func flushIfActive() {
        if UIApplication.shared.applicationState == .active { flush() }
    }

    /// Push buffered GPS fixes into the web app, in chunks so a long locked period doesn't freeze the page.
    func flush() {
        guard pageReady, let web = webView else { return }
        let fixes = LocationService.shared.drain()
        guard !fixes.isEmpty else { return }
        let enc = JSONEncoder()
        stride(from: 0, to: fixes.count, by: 500).forEach { i in
            let chunk = Array(fixes[i..<min(i + 500, fixes.count)])
            guard let data = try? enc.encode(chunk), let json = String(data: data, encoding: .utf8) else { return }
            web.evaluateJavaScript("window.__native && window.__native.fixes(\(json))", completionHandler: nil)
        }
    }

    func send(event: String) {
        DispatchQueue.main.async {
            self.webView?.evaluateJavaScript("window.__native && window.__native.event('\(event)')", completionHandler: nil)
        }
    }
}

struct WebAppView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.userContentController.add(WebBridge.shared, name: "skinav")
        config.allowsInlineMediaPlayback = true
        let web = WKWebView(frame: .zero, configuration: config)
        web.isOpaque = false
        web.backgroundColor = .systemBackground
        web.scrollView.bounces = false
        web.scrollView.isScrollEnabled = false
        web.scrollView.pinchGestureRecognizer?.isEnabled = false
        web.scrollView.minimumZoomScale = 1
        web.scrollView.maximumZoomScale = 1
        web.scrollView.contentInsetAdjustmentBehavior = .never
        #if DEBUG
        if #available(iOS 16.4, *) { web.isInspectable = true }
        #endif
        WebBridge.shared.webView = web
        if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") {
            web.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }
        return web
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
