package com.alonmaltzov.skinav

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context

class SkiNavApp : Application() {
    override fun onCreate() {
        super.onCreate()
        app = this
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(NotificationChannel(CH_TRACK, "Ski day tracking", NotificationManager.IMPORTANCE_LOW).apply {
            description = "Shows your live ski stats while Ski Nav is tracking"
            setShowBadge(false)
        })
        nm.createNotificationChannel(NotificationChannel(CH_BRIEF, "Morning brief", NotificationManager.IMPORTANCE_DEFAULT).apply {
            description = "Your plan for the day, every trip morning"
        })
        nm.createNotificationChannel(NotificationChannel(CH_GAMES, "Games", NotificationManager.IMPORTANCE_HIGH).apply {
            description = "STOPPP flask breaks and the passport check"
            enableVibration(true)
        })
    }

    companion object {
        const val CH_TRACK = "tracking"
        const val CH_BRIEF = "brief"
        const val CH_GAMES = "games"
        lateinit var app: SkiNavApp
        val prefs get() = app.getSharedPreferences("skinav", Context.MODE_PRIVATE)
    }
}
