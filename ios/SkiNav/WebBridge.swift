import SwiftUI
import WebKit

/// Connects the web app (index.html) to native code.
/// JS -> native: window.webkit.messageHandlers.skinav.postMessage({cmd: ...})
/// native -> JS: window.__native.fixes([...]) and window.__native.event(name)
final class WebBridge: NSObject, WKScriptMessageHandler, WKNavigationDelegate {
    func webView(_ w: WKWebView, didFinish n: WKNavigation!) { print("[app] page finished loading") }
    func webView(_ w: WKWebView, didFail n: WKNavigation!, withError e: Error) { print("[app] load failed:", e.localizedDescription) }
    func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) { print("[app] load failed:", e.localizedDescription) }
    func webViewWebContentProcessDidTerminate(_ w: WKWebView) { print("[app] web content crashed, reloading"); w.reload() }
    func webView(_ w: WKWebView, didStartProvisionalNavigation n: WKNavigation!) { pageReady = false }

    /// Pages inside the app (index.html, nyc.html) open in place; anything on the internet opens in Safari.
    func webView(_ w: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = action.request.url else { return decisionHandler(.allow) }
        if url.isFileURL || url.scheme == "about" || url.scheme == "blob" || url.scheme == "data" { return decisionHandler(.allow) }
        if action.navigationType == .linkActivated, ["http", "https", "mailto", "tel", "maps"].contains(url.scheme ?? "") {
            print("[app] opening outside the app:", url.absoluteString)
            UIApplication.shared.open(url)
            return decisionHandler(.cancel)
        }
        decisionHandler(.allow)
    }

    static let shared = WebBridge()
    weak var webView: WKWebView?
    private var pageReady = false

    func userContentController(_ c: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let body = message.body as? [String: Any], let cmd = body["cmd"] as? String else { return }
        switch cmd {
        case "ready":
            pageReady = true
            // the page can be restarted by iOS (memory); if we were tracking, tell it to carry on
            if LocationService.shared.isTracking {
                print("[app] page reloaded during tracking, resuming")
                send(event: "tracking")
            }
            flush()
        case "start":
            var base: SkiTotals?
            if let b = body["base"] as? [String: Any] {
                base = SkiTotals(distM: (b["distM"] as? Double) ?? 0, maxMps: (b["maxMps"] as? Double) ?? 0,
                                 vertM: (b["vertM"] as? Double) ?? 0, elapsedS: (b["elapsedS"] as? Double) ?? 0)
            }
            SkiDay.shared.begin(base: base)
            LocationService.shared.start()
        case "ctx":
            // the resort's lift lines + today's title, so native lift detection matches the page
            SkiDay.shared.setContext(lifts: body["lifts"] as? [[[Double]]], title: body["title"] as? String)
        case "step":
            let st = SkiGlance.Step(label: (body["label"] as? String) ?? "", color: (body["color"] as? String) ?? "lift",
                                    ends: body["ends"] as? [[Double]], nextLift: (body["next"] as? String) ?? "",
                                    nextLiftAt: body["nextAt"] as? [Double], then: (body["then"] as? String) ?? "",
                                    thenColor: (body["thenColor"] as? String) ?? "lift")
            SkiDay.shared.setStep(st, liftLine: body["lift"] as? [[Double]], index: (body["idx"] as? Int) ?? 0)
        case "stop":
            LocationService.shared.stop()
        case "locate":
            LocationService.shared.locate()
        case "compass":
            LocationService.shared.compass((body["on"] as? Bool) ?? false)
        case "log":
            print("[web]", body["msg"] ?? "")
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

    func js(_ code: String) {
        DispatchQueue.main.async { self.webView?.evaluateJavaScript(code, completionHandler: nil) }
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
        // forward JS errors and console output to the Xcode console
        let logJS = """
        (function(){
          const post = m => { try { window.webkit.messageHandlers.skinav.postMessage({cmd:'log', msg: String(m).slice(0, 800)}); } catch(e){} };
          window.addEventListener('error', e => post('ERROR ' + e.message + ' @' + (e.filename||'').split('/').pop() + ':' + e.lineno));
          window.addEventListener('unhandledrejection', e => post('REJECT ' + (e.reason && (e.reason.stack || e.reason))));
          ['error','warn'].forEach(k => { const o = console[k]; console[k] = function(){ post(k.toUpperCase() + ' ' + Array.from(arguments).join(' ')); o.apply(console, arguments); }; });
          document.addEventListener('DOMContentLoaded', () => post('DOM ready, title=' + document.title));
          window.addEventListener('load', () => post('page loaded, map=' + !!document.querySelector('.maplibregl-canvas')));
        })();
        """
        config.userContentController.addUserScript(WKUserScript(source: logJS, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        // Automated QA: launched with -qaTour (by CI or Xcode scheme arguments) the app walks through every screen by itself
        if ProcessInfo.processInfo.arguments.contains("-qaTour"),
           let url = Bundle.main.url(forResource: "qa-tour", withExtension: "js", subdirectory: "www"),
           let js = try? String(contentsOf: url, encoding: .utf8) {
            print("[app] QA tour enabled")
            config.userContentController.addUserScript(WKUserScript(source: "window.__QA_WAIT=2500;\n" + js, injectionTime: .atDocumentEnd, forMainFrameOnly: true))
        }
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
        web.navigationDelegate = WebBridge.shared
        if let url = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") {
            print("[app] loading", url.path, (try? FileManager.default.attributesOfItem(atPath: url.path)[.size]) ?? "?")
            web.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        } else {
            print("[app] ERROR www/index.html is missing from the app bundle. Run ./setup.sh again.")
        }
        return web
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
