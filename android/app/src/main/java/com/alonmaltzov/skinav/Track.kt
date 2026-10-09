package com.alonmaltzov.skinav

import android.location.Location
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * Shared tracking state: fixes collected by TrackingService wait here until the page is visible to take them
 * (with the screen off the page is asleep), and are also saved to a day log on disk.
 */
object Track {
    @Volatile var tracking = false
    private val pending = ArrayList<JSONObject>()
    var distM = 0.0; private set
    var speedMps = 0.0; private set
    var maxMps = 0.0; private set
    private var lastGood: Location? = null
    /** called on the main thread after new fixes arrive (MainActivity flushes them into the page) */
    var onFixes: (() -> Unit)? = null

    fun begin(baseDistM: Double, baseMaxMps: Double) {
        distM = baseDistM; maxMps = baseMaxMps; speedMps = 0.0; lastGood = null
        tracking = true
    }

    fun end() { tracking = false; speedMps = 0.0 }

    fun fixJson(l: Location): JSONObject = JSONObject().apply {
        put("lat", l.latitude); put("lon", l.longitude)
        put("acc", if (l.hasAccuracy()) l.accuracy.toDouble() else 999.0)
        put("alt", if (l.hasAltitude()) l.altitude else JSONObject.NULL)
        put("speed", if (l.hasSpeed()) l.speed.toDouble() else JSONObject.NULL)
        put("heading", if (l.hasBearing()) l.bearing.toDouble() else JSONObject.NULL)
        put("t", l.time.toDouble())
    }

    fun add(locs: List<Location>) {
        val js = locs.map { fixJson(it) }
        synchronized(pending) { pending.addAll(js) }
        for (l in locs) {
            if (l.hasSpeed()) { speedMps = l.speed.toDouble(); if (speedMps > maxMps && l.accuracy <= 30) maxMps = speedMps }
            if (l.accuracy <= 30) {
                lastGood?.let { val d = it.distanceTo(l).toDouble(); if (d > 3 && d < 500) distM += d }
                lastGood = l
            }
        }
        save(js)
    }

    fun drain(): List<JSONObject> = synchronized(pending) { val out = ArrayList(pending); pending.clear(); out }

    private fun dayFile(): File {
        val day = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
        return File(SkiNavApp.app.filesDir, "track-$day.jsonl")
    }

    private fun save(js: List<JSONObject>) {
        try {
            val f = dayFile()
            if (!f.exists()) Log.i("SkiNav", "day log started: ${f.name}")
            f.appendText(js.joinToString("") { it.toString() + "\n" })
        } catch (e: Exception) { Log.w("SkiNav", "track save failed", e) }
    }

    fun clearSaved() {
        if (tracking) return
        val n = SkiNavApp.app.filesDir.listFiles()?.count { it.name.startsWith("track-") && it.name.endsWith(".jsonl") && it.delete() } ?: 0
        synchronized(pending) { pending.clear() }
        Log.i("SkiNav", "cleared $n saved track files")
    }

    fun toArray(list: List<JSONObject>) = JSONArray().also { a -> list.forEach { a.put(it) } }
}
