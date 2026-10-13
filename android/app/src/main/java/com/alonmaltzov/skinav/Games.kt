package com.alonmaltzov.skinav

import android.app.PendingIntent
import android.content.Intent
import android.location.Location
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import org.json.JSONObject
import java.util.Calendar

/** Games that must work with the phone locked: STOPPP (3 a day, after 3 minutes on a lift) and the
 *  passport check (first crossing into Switzerland before noon). The page sends the times and names. */
object Games {
    private data class Stop(val n: Int, val at: Long, val who: String)
    private var stops = listOf<Stop>()
    private var stopOn = true
    private var borderOn = true
    private var border = listOf<DoubleArray>()
    private var day = ""
    private val hist = ArrayDeque<Triple<Long, Double, Float>>()   // time, altitude, speed
    private var liftSince: Long? = null
    private var lastClimb = 0L
    var onEvent: ((String) -> Unit)? = null

    @Synchronized fun configure(b: JSONObject) {
        b.optJSONObject("on")?.let { stopOn = it.optBoolean("stop", true); borderOn = it.optBoolean("border", true) }
        val a = b.optJSONArray("stops")
        stops = (0 until (a?.length() ?: 0)).mapNotNull { i -> a!!.optJSONObject(i)?.let { Stop(it.optInt("n"), it.optLong("at"), it.optString("who", "Someone’s")) } }
        val br = b.optJSONArray("border")
        border = (0 until (br?.length() ?: 0)).mapNotNull { i -> br!!.optJSONArray(i)?.let { doubleArrayOf(it.optDouble(0), it.optDouble(1)) } }
        day = b.optString("day", "")
    }

    private fun fired(k: String) = SkiNavApp.prefs.getBoolean("game-$day-$k", false)
    private fun mark(k: String) = SkiNavApp.prefs.edit().putBoolean("game-$day-$k", true).apply()

    /** riding a lift: steady climb (30 m in the last minute) at lift speed */
    private fun climbing(l: Location): Boolean {
        if (!l.hasAltitude()) return false
        hist.addLast(Triple(l.time, l.altitude, if (l.hasSpeed()) l.speed else -1f))
        while (hist.isNotEmpty() && l.time - hist.first().first > 70_000) hist.removeFirst()
        val old = hist.firstOrNull { l.time - it.first >= 50_000 } ?: return false
        val sp = if (l.hasSpeed()) l.speed else 2f
        return l.altitude - old.second >= 30 && sp in 0.8f..9f
    }

    @Synchronized fun onFix(ctx: android.content.Context, l: Location) {
        if (day.isEmpty() || l.accuracy > 30) return
        val now = System.currentTimeMillis()
        if (now - l.time > 120_000) return
        val hour = Calendar.getInstance().apply { timeInMillis = l.time }.get(Calendar.HOUR_OF_DAY)
        if (climbing(l)) { lastClimb = l.time; if (liftSince == null) liftSince = l.time }
        else if (l.time - lastClimb > 40_000) liftSince = null
        val since = liftSince
        if (stopOn && hour < 16 && since != null && l.time - since >= 180_000) {
            stops.firstOrNull { l.time >= it.at && !fired("stop${it.n}") }?.let { s ->
                mark("stop${s.n}")
                notify(ctx, 7100 + s.n, "STOPPP 🥃", "${s.who} round: flask out at the top of this lift.")
                onEvent?.invoke("stop:${s.n}")
            }
        }
        if (borderOn && hour < 12 && !fired("swiss") && swiss(l.latitude, l.longitude)) {
            mark("swiss")
            notify(ctx, 7200, "Welcome to Switzerland 🇨🇭", "Passport check: who crossed first? Open Ski Nav to see.")
        }
    }

    private fun swiss(lat: Double, lon: Double): Boolean {
        if (border.size < 2) return false
        for (i in 0 until border.size - 1) {
            val (a0, o0) = border[i][0] to border[i][1]; val (a1, o1) = border[i + 1][0] to border[i + 1][1]
            if (lat <= a1) return lon > o0 + (o1 - o0) * maxOf(0.0, (lat - a0) / (a1 - a0))
        }
        return lon > border.last()[1]
    }

    private fun notify(ctx: android.content.Context, id: Int, title: String, body: String) {
        val open = PendingIntent.getActivity(ctx, id, Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        val n = NotificationCompat.Builder(ctx, SkiNavApp.CH_GAMES).setSmallIcon(R.drawable.ic_stat)
            .setContentTitle(title).setContentText(body).setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_HIGH).setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setVibrate(longArrayOf(0, 300, 120, 300, 120, 600)).setAutoCancel(true).setContentIntent(open).build()
        NotificationManagerCompat.from(ctx).notifySafe(id, n)
        Log.i("SkiNav", "games: $title $body")
    }
}
