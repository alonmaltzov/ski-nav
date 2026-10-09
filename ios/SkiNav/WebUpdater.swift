import Foundation

/// Over-the-air updates for the web part of the app (the map, plan, screens).
/// The app opens instantly with the newest copy it has (downloaded or bundled), then checks the website in the background.
/// A newer version is saved and used the next time the app opens. Offline (on the mountain) it just keeps using what it has.
/// Native parts (GPS, lock screen, watch) still come with an Xcode build.
enum WebUpdater {
    static let base = URL(string: "https://alonmaltzov.github.io/ski-nav/")!
    static let pages = ["index.html", "nyc.html"]
    static var dir: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("www", isDirectory: true)
    }
    private static let defaults = UserDefaults.standard
    /// QA runs always test the code that was built, never a download.
    static var disabled: Bool { ProcessInfo.processInfo.arguments.contains(where: { $0.hasPrefix("-qa") || $0 == "-noWebUpdate" }) }

    /// The page to open: the downloaded copy when it's newer than the one inside the app, else the bundled one.
    static func startPage() -> (url: URL, fromDownload: Bool)? {
        guard let bundled = Bundle.main.url(forResource: "index", withExtension: "html", subdirectory: "www") else { return nil }
        let cached = dir.appendingPathComponent("index.html")
        if !disabled, pages.allSatisfy({ FileManager.default.fileExists(atPath: dir.appendingPathComponent($0).path) }),
           let got = defaults.object(forKey: "web.downloadedAt") as? Date,
           let built = (try? FileManager.default.attributesOfItem(atPath: bundled.path)[.modificationDate]) as? Date,
           got > built {
            return (cached, true)
        }
        return (bundled, false)
    }

    /// The downloaded copy didn't start: throw it away so the next launch uses the bundled one.
    static func discardDownload() {
        try? FileManager.default.removeItem(at: dir)
        defaults.removeObject(forKey: "web.downloadedAt")
        for p in pages { defaults.removeObject(forKey: "web.etag." + p) }
        print("[app] downloaded web app didn't start; using the built-in one")
    }

    /// Check the website for a newer version (every time the app opens, at most every 2 minutes). Uses ETags, so an unchanged page costs almost nothing.
    static func checkForUpdate(force: Bool = false) {
        guard !disabled else { return }
        if !force, let last = defaults.object(forKey: "web.checkedAt") as? Date, Date().timeIntervalSince(last) < 120 { return }
        defaults.set(Date(), forKey: "web.checkedAt")
        Task.detached(priority: .background) {
            var fresh: [String: (Data, String?)] = [:]
            for p in pages {
                var req = URLRequest(url: base.appendingPathComponent(p), cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 60)
                let haveAll = pages.allSatisfy { FileManager.default.fileExists(atPath: dir.appendingPathComponent($0).path) }
                if haveAll, let et = defaults.string(forKey: "web.etag." + p) { req.setValue(et, forHTTPHeaderField: "If-None-Match") }
                guard let (data, resp) = try? await URLSession.shared.data(for: req), let http = resp as? HTTPURLResponse else { print("[app] web update check: offline"); return }
                if http.statusCode == 304 { continue }
                // only accept a complete app page
                guard http.statusCode == 200, data.count > 500_000,
                      let tail = String(data: data.suffix(4000), encoding: .utf8), tail.contains("</html>"),
                      String(decoding: data, as: UTF8.self).contains("window.__ski") else { print("[app] web update check: bad download for", p); return }
                fresh[p] = (data, http.value(forHTTPHeaderField: "ETag"))
            }
            guard !fresh.isEmpty else { print("[app] web app is up to date"); return }
            do {
                try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
                // pages that didn't change still need a copy in the folder (first download, or only one changed)
                for p in pages where fresh[p] == nil && !FileManager.default.fileExists(atPath: dir.appendingPathComponent(p).path) {
                    if let b = Bundle.main.url(forResource: (p as NSString).deletingPathExtension, withExtension: "html", subdirectory: "www") {
                        try FileManager.default.copyItem(at: b, to: dir.appendingPathComponent(p))
                    }
                }
                for (p, (data, etag)) in fresh {
                    try data.write(to: dir.appendingPathComponent(p), options: .atomic)
                    if let e = etag { defaults.set(e, forKey: "web.etag." + p) }
                }
                defaults.set(Date(), forKey: "web.downloadedAt")
                print("[app] web update downloaded:", fresh.keys.sorted().joined(separator: ", "))
                // offer it right away (the page shows "New version ready · Update")
                await MainActor.run { WebBridge.shared.send(event: "updateReady") }
            } catch {
                print("[app] web update could not be saved:", error.localizedDescription)
            }
        }
    }
}
