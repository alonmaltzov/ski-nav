package com.alonmaltzov.skinav

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import org.json.JSONArray
import org.json.JSONObject
import java.util.Calendar
import java.util.Locale

/**
 * The guide on Android, all on the phone: Android's text-to-speech for the brief, Android speech recognition
 * for Ask, and Android alarms for the morning notification. Events go back to the page through window.__guide.on.
 */
class Guide(private val ctx: Context, private val emit: (JSONObject) -> Unit) {
    private var tts: TextToSpeech? = null
    private var ttsReady = false
    private var parts: List<String> = emptyList()
    private var at = 0
    private var waiting: (() -> Unit)? = null

    private fun ev(type: String, vararg kv: Pair<String, Any?>) = emit(JSONObject().apply { put("type", type); kv.forEach { put(it.first, it.second) } })

    private fun withTts(go: () -> Unit) {
        if (ttsReady) { go(); return }
        waiting = go
        if (tts != null) return
        tts = TextToSpeech(ctx) { status ->
            ttsReady = status == TextToSpeech.SUCCESS
            if (!ttsReady) { ev("error", "msg" to "This phone has no voice installed. Add one in Settings › Text-to-speech."); return@TextToSpeech }
            val t = tts!!
            val loc = Locale.US
            if (t.isLanguageAvailable(loc) >= TextToSpeech.LANG_AVAILABLE) t.language = loc
            // the best-quality English voice installed (network voices are skipped: the mountain has no signal)
            t.voices?.filter { it.locale.language == "en" && !it.isNetworkConnectionRequired }?.maxByOrNull { it.quality }?.let { t.voice = it }
            t.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                override fun onStart(id: String) { id.removePrefix("p").toIntOrNull()?.let { at = it; ev("part", "i" to it) } }
                override fun onDone(id: String) { if (id == "p${parts.size - 1}") { parts = emptyList(); ev("done") } }
                @Deprecated("old api") override fun onError(id: String) {}
            })
            waiting?.invoke(); waiting = null
        }
    }

    fun speak(b: JSONObject) {
        if (b.optBoolean("stop")) { parts = emptyList(); tts?.stop(); return }
        if (b.has("pause")) {
            // Android voices can't pause mid-sentence: stop, and resume from the sentence we were on
            if (b.optBoolean("pause")) tts?.stop() else if (parts.isNotEmpty()) say(at)
            return
        }
        val arr: JSONArray = b.optJSONArray("parts") ?: return
        parts = (0 until arr.length()).map { arr.optString(it) }
        if (parts.isEmpty()) return
        stopListening()
        withTts { say(0) }
    }

    private fun say(from: Int) {
        val t = tts ?: return
        t.stop()
        for (i in from until parts.size) {
            t.speak(parts[i], if (i == from) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD, Bundle(), "p$i")
            t.playSilentUtterance(120, TextToSpeech.QUEUE_ADD, "gap$i")
        }
    }

    // ---- listening ----
    private var rec: SpeechRecognizer? = null

    fun listen(on: Boolean) {
        if (!on) { rec?.stopListening(); return }
        if (!SpeechRecognizer.isRecognitionAvailable(ctx)) { ev("error", "msg" to "Speech recognition isn't available on this phone."); return }
        tts?.stop()
        rec?.destroy()
        val r = SpeechRecognizer.createSpeechRecognizer(ctx); rec = r
        r.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(p: Bundle?) { ev("listening", "on" to true) }
            override fun onPartialResults(p: Bundle?) { best(p)?.let { ev("heard", "text" to it, "final" to false) } }
            override fun onResults(p: Bundle?) { ev("heard", "text" to (best(p) ?: ""), "final" to true); ev("listening", "on" to false) }
            override fun onError(e: Int) { ev("listening", "on" to false); if (e != SpeechRecognizer.ERROR_NO_MATCH && e != SpeechRecognizer.ERROR_SPEECH_TIMEOUT) Log.w("SkiNav", "speech error $e") }
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(v: Float) {}
            override fun onBufferReceived(b: ByteArray?) {}
            override fun onEndOfSpeech() {}
            override fun onEvent(t: Int, p: Bundle?) {}
        })
        r.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
        })
    }

    private fun best(p: Bundle?) = p?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
    private fun stopListening() { rec?.cancel() }

    fun destroy() { tts?.shutdown(); rec?.destroy() }

    companion object {
        /** Morning brief alarms for each trip day at the chosen time (local time). Saved so a reboot can set them again. */
        fun schedule(ctx: Context, b: JSONObject) {
            SkiNavApp.prefs.edit().putString("brief.schedule", b.toString()).apply()
            val am = ctx.getSystemService(AlarmManager::class.java)
            for (i in 0 until 21) am.cancel(pending(ctx, i, b))
            if (!b.optBoolean("on", true)) return
            val dates = b.optJSONArray("dates") ?: return
            val hm = b.optString("time", "08:30").split(":").mapNotNull { it.toIntOrNull() }
            var n = 0
            for (i in 0 until minOf(dates.length(), 21)) {
                val d = dates.optJSONArray(i) ?: continue
                if (d.length() != 3) continue
                val c = Calendar.getInstance().apply {
                    set(d.getInt(0), d.getInt(1) - 1, d.getInt(2), hm.getOrElse(0) { 8 }, hm.getOrElse(1) { 30 }, 0); set(Calendar.MILLISECOND, 0)
                }
                if (c.timeInMillis < System.currentTimeMillis()) continue
                // inexact by a few minutes at most; no special alarm permission needed
                am.setWindow(AlarmManager.RTC_WAKEUP, c.timeInMillis, 5 * 60_000L, pending(ctx, i, b))
                n++
            }
            Log.i("SkiNav", "morning brief scheduled for $n day(s)")
        }

        private fun pending(ctx: Context, i: Int, b: JSONObject): PendingIntent =
            PendingIntent.getBroadcast(ctx, 100 + i, Intent(ctx, BriefReceiver::class.java)
                .putExtra("title", b.optString("title", "Your morning brief is ready"))
                .putExtra("body", b.optString("body", "Tap to listen.")),
                PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
    }
}

class BriefReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        val open = PendingIntent.getActivity(ctx, 2, Intent(ctx, MainActivity::class.java).putExtra("openBrief", true)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        val n = NotificationCompat.Builder(ctx, SkiNavApp.CH_BRIEF)
            .setSmallIcon(R.drawable.ic_stat)
            .setContentTitle(intent.getStringExtra("title") ?: "Your morning brief is ready")
            .setContentText(intent.getStringExtra("body") ?: "Tap to listen.")
            .setContentIntent(open)
            .setAutoCancel(true)
            .build()
        NotificationManagerCompat.from(ctx).notifySafe(8, n)
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return
        SkiNavApp.prefs.getString("brief.schedule", null)?.let { Guide.schedule(ctx, JSONObject(it)) }
    }
}
