package com.alonmaltzov.skinav

import android.Manifest
import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.PackageManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.provider.Settings
import android.util.Log
import android.view.View
import android.webkit.ConsoleMessage
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import com.google.android.gms.tasks.CancellationTokenSource
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.File

/**
 * The app screen: the same web app as the iPhone (index.html), with an Android bridge that speaks the
 * iPhone bridge's language (window.webkit.messageHandlers.skinav.postMessage), so the page needs no Android branches.
 */
class MainActivity : ComponentActivity(), SensorEventListener {
    private lateinit var web: WebView
    private val main = Handler(Looper.getMainLooper())
    private var pageReady = false
    private var resumed = false
    private var pendingJoin: String? = null
    private var pendingBrief = false
    private var qaTour = false
    private var usingDownload = false
    private lateinit var guide: Guide

    // ---------- permissions ----------
    private var afterPerms: ((Boolean) -> Unit)? = null
    private val permLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { res ->
        val cb = afterPerms; afterPerms = null
        cb?.invoke(res.values.firstOrNull() ?: false)
    }
    private fun has(p: String) = ContextCompat.checkSelfPermission(this, p) == PackageManager.PERMISSION_GRANTED
    private fun withPerms(perms: List<String>, then: (Boolean) -> Unit) {
        val missing = perms.filter { !has(it) }
        if (missing.isEmpty()) { then(true); return }
        afterPerms = { then(has(perms.first())) }
        permLauncher.launch(missing.toTypedArray())
    }
    private val locationPerms = listOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
    private val notifPerm = if (Build.VERSION.SDK_INT >= 33) listOf(Manifest.permission.POST_NOTIFICATIONS) else emptyList()

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        qaTour = intent.getBooleanExtra("qaTour", false)
        WebUpdater.disabled = qaTour || intent.getBooleanExtra("noWebUpdate", false)
        guide = Guide(this) { js("window.__guide && window.__guide.on(${it})") }

        web = WebView(this)
        web.setBackgroundColor(0xFFF4F7F9.toInt())
        web.overScrollMode = View.OVER_SCROLL_NEVER
        with(web.settings) {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            mediaPlaybackRequiresUserGesture = false
            setSupportZoom(false)
            builtInZoomControls = false
            textZoom = 100
        }
        WebView.setWebContentsDebuggingEnabled(true)
        web.addJavascriptInterface(Bridge(), "SkiNavAndroid")
        web.webViewClient = Client()
        web.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(m: ConsoleMessage): Boolean {
                if (m.messageLevel() == ConsoleMessage.MessageLevel.ERROR) Log.w("SkiNav-web", "${m.message()} @${m.sourceId().substringAfterLast('/')}:${m.lineNumber()}")
                return true
            }
        }
        setContentView(web)
        // Android 15 draws apps edge to edge: keep the page clear of the status bar and gesture bar
        ViewCompat.setOnApplyWindowInsetsListener(web) { v, insets ->
            val b = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            v.setPadding(b.left, b.top, b.right, b.bottom); insets
        }

        handleIntent(intent)
        usingDownload = WebUpdater.useDownload(this)
        Log.i("SkiNav", "loading " + if (usingDownload) "downloaded" else "built-in" + " web app")
        web.loadUrl(START)
        if (usingDownload) main.postDelayed({
            if (!pageReady) { WebUpdater.discard(this); usingDownload = false; web.loadUrl(START) }
        }, 15_000)
        Track.onFixes = { if (resumed) flush() }
    }

    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent); setIntent(intent); handleIntent(intent) }

    private fun handleIntent(i: Intent?) {
        if (i == null) return
        if (i.getBooleanExtra("openBrief", false)) { i.removeExtra("openBrief"); if (pageReady) event("openBrief") else pendingBrief = true }
        val u = i.data ?: return
        if (u.scheme == "skinav" && u.host == "join") {
            val code = u.getQueryParameter("c") ?: return
            if (!Regex("^[A-Za-z0-9-]{4,16}$").matches(code)) return
            Log.i("SkiNav", "opened from invite $code")
            if (pageReady) event("join:" + code.uppercase()) else pendingJoin = code.uppercase()
        }
    }

    override fun onResume() {
        super.onResume(); resumed = true
        flush()
        WebUpdater.check(this) { main.post { event("updateReady") } }
    }
    override fun onPause() { resumed = false; super.onPause() }
    override fun onDestroy() { Track.onFixes = null; guide.destroy(); compass(false); super.onDestroy() }

    // ---------- serving the web app ----------
    private inner class Client : WebViewClient() {
        override fun shouldInterceptRequest(view: WebView, req: WebResourceRequest): WebResourceResponse? {
            val u = req.url
            if (u.host != HOST || !(u.path ?: "").startsWith("/www/")) return null
            val name = u.path!!.removePrefix("/www/")
            return try {
                if (name.endsWith(".html")) {
                    val dl = File(WebUpdater.dir(this@MainActivity), name)
                    val html = if (usingDownload && dl.exists()) dl.readText() else assets.open("www/$name").bufferedReader().use { it.readText() }
                    WebResourceResponse("text/html", "utf-8", ByteArrayInputStream(inject(html).toByteArray()))
                } else {
                    val mime = when { name.endsWith(".js") -> "text/javascript"; name.endsWith(".json") -> "application/json"; name.endsWith(".css") -> "text/css"; else -> "application/octet-stream" }
                    WebResourceResponse(mime, "utf-8", assets.open("www/$name"))
                }
            } catch (e: Exception) { Log.w("SkiNav", "missing $name"); null }
        }

        override fun shouldOverrideUrlLoading(view: WebView, req: WebResourceRequest): Boolean {
            val u = req.url
            if (u.host == HOST) return false
            // WhatsApp, Splitwise, maps, phone, mail: open in their own apps
            try { startActivity(Intent(Intent.ACTION_VIEW, u)) } catch (e: Exception) { Log.w("SkiNav", "nothing opens $u") }
            return true
        }

        override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) { pageReady = false }

        override fun onRenderProcessGone(view: WebView, detail: android.webkit.RenderProcessGoneDetail): Boolean {
            Log.w("SkiNav", "web content crashed, reloading"); view.loadUrl(START); return true
        }
    }

    /** The page talks to "window.webkit.messageHandlers.skinav" like on iPhone; this makes that name exist on Android. */
    private fun inject(html: String): String {
        val shim = StringBuilder("<script>window.__ANDROID=true;window.webkit={messageHandlers:{skinav:{postMessage:function(m){try{SkiNavAndroid.post(JSON.stringify(m))}catch(e){}}}}};" +
            "(function(){var p=function(m){try{SkiNavAndroid.post(JSON.stringify({cmd:'log',msg:String(m).slice(0,800)}))}catch(e){}};" +
            "addEventListener('error',function(e){p('ERROR '+e.message+' @'+(e.filename||'').split('/').pop()+':'+e.lineno)});" +
            "addEventListener('load',function(){p('page loaded, map='+!!document.querySelector('.maplibregl-canvas'))});})();")
        if (qaTour) shim.append("window.__QA_TOUR=true;window.__QA_WAIT=2500;")
        shim.append("</script>")
        var out = html.replaceFirst("<head>", "<head>$shim")
        if (qaTour) {
            val tour = try { assets.open("www/qa-tour.js").bufferedReader().use { it.readText() } } catch (e: Exception) { "" }
            out = out.replaceFirst(Regex("</body>(?![\\s\\S]*</body>)"), Regex.escapeReplacement("<script>$tour</script></body>"))
        }
        return out
    }

    // ---------- page <-> app ----------
    private fun js(code: String) = main.post { web.evaluateJavascript(code, null) }
    private fun event(name: String) = js("window.__native && window.__native.event(${JSONObject.quote(name)})")

    private fun flush() {
        if (!pageReady) return
        val fixes = Track.drain()
        if (fixes.isEmpty()) return
        fixes.chunked(500).forEach { js("window.__native && window.__native.fixes(${Track.toArray(it)})") }
    }

    inner class Bridge {
        @JavascriptInterface
        fun post(json: String) {
            val b = try { JSONObject(json) } catch (e: Exception) { return }
            main.post { handle(b) }
        }
    }

    private fun handle(b: JSONObject) {
        when (b.optString("cmd")) {
            "ready" -> {
                pageReady = true
                if (Track.tracking) { Log.i("SkiNav", "page reloaded during tracking, resuming"); event("tracking") }
                flush()
                pendingJoin?.let { pendingJoin = null; event("join:$it") }
                if (pendingBrief) { pendingBrief = false; event("openBrief") }
            }
            "log" -> Log.i("SkiNav-web", b.optString("msg"))
            "start" -> withPerms(locationPerms + notifPerm) { ok ->
                if (!ok) { event("denied"); return@withPerms }
                val base = b.optJSONObject("base")
                Track.begin(base?.optDouble("distM", 0.0) ?: 0.0, base?.optDouble("maxMps", 0.0) ?: 0.0)
                ContextCompat.startForegroundService(this, Intent(this, TrackingService::class.java))
                askBatteryOnce()
            }
            "stop" -> { if (Track.tracking) startService(Intent(this, TrackingService::class.java).setAction(TrackingService.ACTION_STOP)); flush() }
            "locate" -> withPerms(locationPerms) { ok -> if (ok) locate() else event("denied") }
            "compass" -> compass(b.optBoolean("on"))
            "speak" -> guide.speak(b)
            "listen" -> if (b.optBoolean("on")) withPerms(listOf(Manifest.permission.RECORD_AUDIO)) { ok ->
                if (ok) guide.listen(true) else js("window.__guide && window.__guide.on({type:'error',msg:'To talk to me, allow the microphone for Ski Nav in Settings.'})")
            } else guide.listen(false)
            "think" -> js("window.__guide && window.__guide.on({type:'thought'})")   // open questions: iPhone only for now
            "briefSchedule" -> withPerms(notifPerm.ifEmpty { listOf(Manifest.permission.INTERNET) }) { Guide.schedule(this, b) }
            "personalVoice" -> js("window.__guide && window.__guide.on({type:'error',msg:'My voice is iPhone only. I\\u2019ll use the Android voice.'})")
            "reloadApp" -> { usingDownload = WebUpdater.useDownload(this); web.loadUrl(START) }
            "clear" -> Track.clearSaved()
            "group" -> GroupLink.configure(b)
            // "ctx", "step", "plan": lift lines, current step and the watch plan are iPhone/Watch only for now
        }
    }

    @SuppressLint("MissingPermission")
    private fun locate() {
        val c = LocationServices.getFusedLocationProviderClient(this)
        c.lastLocation.addOnSuccessListener { l -> if (l != null && System.currentTimeMillis() - l.time < 20_000) js("window.__native && window.__native.located(${Track.fixJson(l)})") }
        c.getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY, CancellationTokenSource().token)
            .addOnSuccessListener { l -> if (l != null) js("window.__native && window.__native.located(${Track.fixJson(l)})") }
    }

    /** Samsung, Xiaomi and others stop background apps to save battery: ask once to leave Ski Nav running. */
    @SuppressLint("BatteryLife")
    private fun askBatteryOnce() {
        val pm = getSystemService(PowerManager::class.java)
        if (pm.isIgnoringBatteryOptimizations(packageName) || SkiNavApp.prefs.getBoolean("askedBattery", false) || qaTour) return
        SkiNavApp.prefs.edit().putBoolean("askedBattery", true).apply()
        try { startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName"))) } catch (_: Exception) {}
    }

    // ---------- compass ----------
    private var compassOn = false
    private var lastHeading = 0L
    private fun compass(on: Boolean) {
        val sm = getSystemService(SensorManager::class.java)
        if (on == compassOn) return
        compassOn = on
        if (!on) { sm.unregisterListener(this); return }
        val s = sm.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
        if (s == null) { event("nocompass"); compassOn = false; return }
        sm.registerListener(this, s, SensorManager.SENSOR_DELAY_UI)
    }
    private val rot = FloatArray(9); private val ori = FloatArray(3)
    override fun onSensorChanged(e: SensorEvent) {
        val now = System.currentTimeMillis(); if (now - lastHeading < 100) return; lastHeading = now
        SensorManager.getRotationMatrixFromVector(rot, e.values)
        SensorManager.getOrientation(rot, ori)
        val deg = (Math.toDegrees(ori[0].toDouble()) + 360) % 360
        js("window.__native && window.__native.heading && window.__native.heading($deg)")
    }
    override fun onAccuracyChanged(s: Sensor?, a: Int) {}

    companion object {
        const val HOST = "appassets.androidplatform.net"
        const val START = "https://$HOST/www/index.html"
    }
}
