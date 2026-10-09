package com.alonmaltzov.skinav

import android.content.Context
import android.util.Log
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

/**
 * Over-the-air updates for the screens (same as the iPhone app): open with the newest copy we have, then check
 * the website in the background. A newer version is saved and offered with "New version ready · Update".
 */
object WebUpdater {
    private const val BASE = "https://alonmaltzov.github.io/ski-nav/"
    val pages = listOf("index.html", "nyc.html")
    private val p get() = SkiNavApp.prefs
    var disabled = false

    fun dir(ctx: Context) = File(ctx.filesDir, "www")

    /** Use the downloaded pages when they're newer than this install of the app. */
    fun useDownload(ctx: Context): Boolean {
        if (disabled) return false
        val got = p.getLong("web.downloadedAt", 0)
        val installed = ctx.packageManager.getPackageInfo(ctx.packageName, 0).lastUpdateTime
        return got > installed && pages.all { File(dir(ctx), it).exists() }
    }

    fun discard(ctx: Context) {
        dir(ctx).deleteRecursively()
        p.edit().remove("web.downloadedAt").apply { pages.forEach { remove("web.etag.$it") } }.apply()
        Log.w("SkiNav", "downloaded web app didn't start; using the built-in one")
    }

    fun check(ctx: Context, onReady: () -> Unit) {
        if (disabled) return
        val now = System.currentTimeMillis()
        if (now - p.getLong("web.checkedAt", 0) < 120_000) return
        p.edit().putLong("web.checkedAt", now).apply()
        thread(name = "web-update") {
            val d = dir(ctx)
            val haveAll = pages.all { File(d, it).exists() }
            val fresh = HashMap<String, Pair<ByteArray, String?>>()
            for (page in pages) {
                try {
                    val c = URL(BASE + page).openConnection() as HttpURLConnection
                    c.connectTimeout = 20000; c.readTimeout = 60000; c.useCaches = false
                    if (haveAll) p.getString("web.etag.$page", null)?.let { c.setRequestProperty("If-None-Match", it) }
                    val code = c.responseCode
                    if (code == 304) { c.disconnect(); continue }
                    if (code != 200) { Log.w("SkiNav", "web update: HTTP $code for $page"); return@thread }
                    val data = c.inputStream.use { it.readBytes() }
                    val tail = String(data.copyOfRange(maxOf(0, data.size - 4000), data.size))
                    if (data.size < 500_000 || !tail.contains("</html>") || !String(data).contains("window.__ski")) { Log.w("SkiNav", "web update: bad download for $page"); return@thread }
                    fresh[page] = data to c.getHeaderField("ETag")
                    c.disconnect()
                } catch (e: Exception) { Log.i("SkiNav", "web update check: offline"); return@thread }
            }
            if (fresh.isEmpty()) { Log.i("SkiNav", "web app is up to date"); return@thread }
            d.mkdirs()
            for (page in pages) if (fresh[page] == null && !File(d, page).exists()) {
                ctx.assets.open("www/$page").use { i -> File(d, page).outputStream().use { i.copyTo(it) } }
            }
            val e = p.edit()
            for ((page, v) in fresh) {
                val tmp = File(d, "$page.tmp"); tmp.writeBytes(v.first); tmp.renameTo(File(d, page))
                v.second?.let { e.putString("web.etag.$page", it) }
            }
            e.putLong("web.downloadedAt", System.currentTimeMillis()).apply()
            Log.i("SkiNav", "web update downloaded: " + fresh.keys.sorted().joined())
            onReady()
        }
    }

    private fun List<String>.joined() = joinToString(", ")
}
