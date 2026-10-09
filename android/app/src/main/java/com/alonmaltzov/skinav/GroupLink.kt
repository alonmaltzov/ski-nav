package com.alonmaltzov.skinav

import android.location.Location
import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.util.Calendar
import kotlin.concurrent.thread

/**
 * Shares this phone's position with the trip group from the tracking service, so friends see you with the
 * phone locked. Same rules as the iPhone: only while tracking, at most every 30 s, never after the stop hour
 * (6 pm on trip days), nothing when sharing is off.
 */
object GroupLink {
    private val p get() = SkiNavApp.prefs
    @Volatile private var lastPost = 0L
    @Volatile private var inFlight = false

    fun configure(b: JSONObject) {
        p.edit()
            .putString("group.url", b.optString("url"))
            .putString("group.key", b.optString("key"))
            .putString("group.secret", b.optString("secret"))
            .putBoolean("group.sharing", b.optBoolean("sharing", true))
            .putInt("group.stopHour", b.optInt("stopHour", 18))
            .apply()
        Log.i("SkiNav", "group: " + if (b.optString("secret").isEmpty()) "none" else if (b.optBoolean("sharing", true)) "sharing location" else "not sharing")
    }

    fun maybePost(l: Location, km: Double) {
        val url = p.getString("group.url", "") ?: ""
        val key = p.getString("group.key", "") ?: ""
        val secret = p.getString("group.secret", "") ?: ""
        val now = System.currentTimeMillis()
        if (secret.isEmpty() || url.isEmpty() || !p.getBoolean("group.sharing", true) || inFlight || now - lastPost < 30_000) return
        if (Calendar.getInstance().get(Calendar.HOUR_OF_DAY) >= p.getInt("group.stopHour", 18)) return
        lastPost = now; inFlight = true
        val body = JSONObject().apply {
            put("p_secret", secret); put("p_lat", l.latitude); put("p_lon", l.longitude)
            put("p_acc", l.accuracy.toDouble()); put("p_speed", if (l.hasSpeed()) l.speed.toDouble() else 0.0)
            put("p_on_lift", false); put("p_km", Math.round(km * 100) / 100.0)
        }
        thread(name = "group-post") {
            try {
                val c = URL(url.trimEnd('/') + "/rest/v1/rpc/post_position").openConnection() as HttpURLConnection
                c.requestMethod = "POST"; c.connectTimeout = 15000; c.readTimeout = 15000; c.doOutput = true
                c.setRequestProperty("apikey", key); c.setRequestProperty("Authorization", "Bearer $key")
                c.setRequestProperty("Content-Type", "application/json")
                c.outputStream.use { it.write(body.toString().toByteArray()) }
                val code = c.responseCode
                if (code >= 300) {
                    Log.w("SkiNav", "group position not sent: HTTP $code")
                    if (code == 400 || code == 403) lastPost = System.currentTimeMillis() + 300_000
                }
                c.disconnect()
            } catch (e: Exception) {
                Log.w("SkiNav", "group position not sent: ${e.message}")
            } finally { inFlight = false }
        }
    }
}
