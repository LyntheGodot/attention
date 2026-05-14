package com.attention.app.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import com.attention.app.MainActivity
import com.attention.app.data.UsageRepository

class UsageMonitorService : AccessibilityService() {
    companion object {
        private const val TAG = "UsageMonitor"
        private const val CHANNEL_ID = "usage_monitor_channel"
        private const val NOTIFICATION_ID = 1002
        const val ACTION_START = "com.attention.app.START_MONITOR"
        const val ACTION_STOP = "com.attention.app.STOP_MONITOR"
        val repository = UsageRepository()
        var isMonitoring = false; private set
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (!isMonitoring || event == null) return
        if (event.eventType == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            val packageName = event.packageName?.toString() ?: return
            if (packageName == "com.android.systemui" || packageName == this.packageName) return
            val appName = try {
                val ai = packageManager.getApplicationInfo(packageName, 0); packageManager.getApplicationLabel(ai).toString()
            } catch (e: PackageManager.NameNotFoundException) { packageName }
            repository.onAppSwitch(packageName, appName)
        }
    }

    override fun onInterrupt() {}

    override fun onServiceConnected() {
        super.onServiceConnected()
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_GENERIC
            notificationTimeout = 100; flags = AccessibilityServiceInfo.DEFAULT
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> { isMonitoring = true; repository.startSession(); startForeground(NOTIFICATION_ID, buildNotification("正在记录手机使用情况...")) }
            ACTION_STOP -> { isMonitoring = false; repository.stopSession(); stopForeground(STOP_FOREGROUND_REMOVE) }
        }
        return START_STICKY
    }

    override fun onCreate() { super.onCreate(); createNotificationChannel() }
    private fun buildNotification(text: String): Notification {
        val pi = PendingIntent.getActivity(this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        return Notification.Builder(this, CHANNEL_ID).setContentTitle("注意力番茄钟 - 监测中")
            .setContentText(text).setSmallIcon(android.R.drawable.ic_dialog_info).setContentIntent(pi).setOngoing(true).build()
    }
    private fun createNotificationChannel() {
        (getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "App 使用监测", NotificationManager.IMPORTANCE_LOW).apply { description = "记录手机应用前台使用情况" })
    }
}
