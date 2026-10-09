package com.alonmaltzov.skinav

import android.annotation.SuppressLint
import android.app.Notification
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.app.ServiceCompat
import com.google.android.gms.location.LocationCallback
import com.google.android.gms.location.LocationRequest
import com.google.android.gms.location.LocationResult
import com.google.android.gms.location.LocationServices
import com.google.android.gms.location.Priority
import java.util.Locale

/**
 * The ski day with the screen off: a foreground service (type location) keeps Google's fused location
 * running about once a second while the phone is locked in a pocket, and shows live stats in its
 * ongoing notification (Android's version of the iPhone lock-screen tracker).
 */
class TrackingService : Service() {
    private val client by lazy { LocationServices.getFusedLocationProviderClient(this) }
    private var lastNotif = 0L

    private val callback = object : LocationCallback() {
        override fun onLocationResult(r: LocationResult) {
            val locs = r.locations
            if (locs.isEmpty()) return
            Track.add(locs)
            locs.lastOrNull { it.accuracy <= 100 }?.let { GroupLink.maybePost(it, Track.distM / 1000) }
            val now = System.currentTimeMillis()
            if (now - lastNotif > 5000) { lastNotif = now; NotificationManagerCompat.from(this@TrackingService).notifySafe(NOTIF_ID, build()) }
            Track.onFixes?.invoke()
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    @SuppressLint("MissingPermission")
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) { stopEverything(); return START_NOT_STICKY }
        val type = if (Build.VERSION.SDK_INT >= 29) ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION else 0
        try {
            ServiceCompat.startForeground(this, NOTIF_ID, build(), type)
        } catch (e: Exception) {
            Log.e("SkiNav", "could not start tracking in the foreground", e); stopSelf(); return START_NOT_STICKY
        }
        val req = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 1000)
            .setMinUpdateIntervalMillis(500)
            .setMinUpdateDistanceMeters(0f)
            .setWaitForAccurateLocation(false)
            .build()
        client.removeLocationUpdates(callback)
        client.requestLocationUpdates(req, callback, Looper.getMainLooper())
        Log.i("SkiNav", "tracking on")
        return START_STICKY
    }

    private fun stopEverything() {
        client.removeLocationUpdates(callback)
        Track.end()
        ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
        stopSelf()
        Log.i("SkiNav", "tracking off")
    }

    override fun onDestroy() { client.removeLocationUpdates(callback); super.onDestroy() }

    private fun build(): Notification {
        val open = PendingIntent.getActivity(this, 0, Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        val stop = PendingIntent.getService(this, 1, Intent(this, TrackingService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE)
        val km = String.format(Locale.US, "%.1f km", Track.distM / 1000)
        val kmh = (Track.speedMps * 3.6).toInt()
        val max = (Track.maxMps * 3.6).toInt()
        return NotificationCompat.Builder(this, SkiNavApp.CH_TRACK)
            .setSmallIcon(R.drawable.ic_stat)
            .setContentTitle("Skiing · $km")
            .setContentText("$kmh km/h now · max $max km/h")
            .setContentIntent(open)
            .addAction(0, "Stop", stop)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(NotificationCompat.CATEGORY_WORKOUT)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    companion object {
        const val NOTIF_ID = 7
        const val ACTION_STOP = "stop"
    }
}

@SuppressLint("MissingPermission")
fun NotificationManagerCompat.notifySafe(id: Int, n: Notification) { try { notify(id, n) } catch (_: SecurityException) {} }
