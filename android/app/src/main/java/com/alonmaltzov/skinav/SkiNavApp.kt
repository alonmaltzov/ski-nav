package com.alonmaltzov.skinav

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.media.AudioAttributes
import android.net.Uri

class SkiNavApp : Application() {
    override fun onCreate() {
        super.onCreate()
        app = this
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel(CH_TRACK, "Ski day tracking", NotificationManager.IMPORTANCE_LOW).apply {
            description = "Shows your live ski stats while Ski-Paz is tracking"
            setShowBadge(false)
        })
        nm.createNotificationChannel(NotificationChannel(CH_BRIEF, "Morning brief", NotificationManager.IMPORTANCE_DEFAULT).apply {
            description = "Your plan for the day, every trip morning"
        })
        nm.deleteNotificationChannel("games")   // replaced by channels with their own sounds
        val attrs = AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION_EVENT).setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build()
        fun gameChannel(id: String, name: String, desc: String, raw: Int?) = nm.createNotificationChannel(NotificationChannel(id, name, NotificationManager.IMPORTANCE_HIGH).apply {
            description = desc; enableVibration(true)
            setSound(raw?.let { Uri.parse("android.resource://$packageName/$it") }, if (raw == null) null else attrs)
        })
        gameChannel(CH_STOP, "STOPPP", "Flask breaks, 3 a day on a long lift", R.raw.sfx_stoppp)
        gameChannel(CH_SWISS, "Passport check", "First into Switzerland in the morning", R.raw.sfx_passport)
        gameChannel(CH_GAMES_QUIET, "Games (app open)", "Games while Ski-Paz is open; the app plays the sound itself", null)
    }

    companion object {
        const val CH_TRACK = "tracking"
        const val CH_BRIEF = "brief"
        const val CH_STOP = "games_stoppp"
        const val CH_SWISS = "games_passport"
        const val CH_GAMES_QUIET = "games_quiet"
        lateinit var app: SkiNavApp
        val prefs get() = app.getSharedPreferences("skinav", Context.MODE_PRIVATE)
    }
}
