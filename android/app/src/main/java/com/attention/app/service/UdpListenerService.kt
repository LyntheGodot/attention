package com.attention.app.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.util.Log
import android.widget.Toast
import com.attention.app.MainActivity
import com.attention.app.data.PairingRepository
import com.attention.app.data.PhoneActivity
import com.attention.app.data.ReportApi
import com.attention.app.data.SessionReport
import com.google.gson.Gson
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class UdpListenerService : Service() {
    companion object {
        private const val TAG = "AttentionService"
        private const val CHANNEL_ID = "attention_channel"
        private const val NOTIFICATION_ID = 1001
        private const val POLL_INTERVAL_MS = 2000L
        const val ACTION_STOP = "com.attention.app.STOP_LISTENER"
    }

    private lateinit var pairingRepo: PairingRepository
    private val reportApi = ReportApi()
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val handler = Handler(Looper.getMainLooper())
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS).readTimeout(5, TimeUnit.SECONDS).build()
    private var currentSessionId: String? = null
    private var sessionStartTimeMs: Long = 0
    private var lastPolledStatus = "idle"
    private var wakeLock: PowerManager.WakeLock? = null
    @Volatile private var polling = false

    override fun onCreate() {
        super.onCreate()
        pairingRepo = PairingRepository(this)
        createNotificationChannel()
        acquireWakeLock()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) { stopSelf(); return START_NOT_STICKY }
        startForeground(NOTIFICATION_ID, buildNotification("等待电脑端指令..."))
        toast("服务已启动，等待配对...")
        scope.launch {
            pairingRepo.pairingInfo.collect { info ->
                if (info.isPaired && !polling) startPolling(info.ip, info.httpPort)
                else if (!info.isPaired) polling = false
            }
        }
        return START_STICKY
    }

    private suspend fun startPolling(pcIp: String, httpPort: Int) {
        polling = true
        Log.i(TAG, "HTTP 轮询启动 → $pcIp:$httpPort")
        toast("HTTP 轮询启动")
        while (polling && scope.isActive) {
            try {
                val status = fetchSessionStatus(pcIp, httpPort)
                val newStatus = status["status"] as? String ?: "idle"
                val sessionId = status["session_id"] as? String ?: ""
                if (newStatus != lastPolledStatus) {
                    Log.i(TAG, "状态变更: $lastPolledStatus → $newStatus")
                    toast("状态: $lastPolledStatus → $newStatus")
                    when {
                        lastPolledStatus == "idle" && newStatus == "active" -> {
                            currentSessionId = sessionId
                            sessionStartTimeMs = System.currentTimeMillis()
                            updateNotification("专注会话进行中...")
                        }
                        lastPolledStatus == "active" && newStatus == "stopped" -> {
                            updateNotification("正在上报数据...")
                            sendReport()
                            currentSessionId = null
                            updateNotification("等待电脑端指令...")
                        }
                    }
                    lastPolledStatus = newStatus
                }
            } catch (e: Exception) { Log.e(TAG, "轮询失败: ${e.message}") }
            delay(POLL_INTERVAL_MS)
        }
        polling = false
    }

    private suspend fun fetchSessionStatus(pcIp: String, httpPort: Int): Map<String, Any> {
        val request = Request.Builder().url("http://$pcIp:$httpPort/session_status").get().build()
        return withContext(Dispatchers.IO) {
            val response = httpClient.newCall(request).execute()
            val body = response.body?.string() ?: "{}"
            @Suppress("UNCHECKED_CAST")
            (Gson().fromJson(body, Map::class.java) as? Map<String, Any>) ?: mapOf("status" to "idle")
        }
    }

    private suspend fun sendReport() {
        val info = pairingRepo.pairingInfo.first()
        if (!info.isPaired || currentSessionId == null) return
        val activities = queryUsageEvents()
        val report = SessionReport(session_id = currentSessionId!!, token = info.token,
            activities = activities, screen_unlocks = 0,
            total_monitored_sec = (System.currentTimeMillis() - sessionStartTimeMs) / 1000)
        Log.i(TAG, "上报 ${report.activities.size} 条手机活动记录")
        toast("上报 ${report.activities.size} 条")
        reportApi.sendReport(info.ip, info.httpPort, report).onSuccess {
            Log.i(TAG, "上报成功"); toast("上报成功")
        }.onFailure {
            Log.e(TAG, "上报失败: ${it.message}"); toast("上报失败: ${it.message}")
        }
    }

    private fun queryUsageEvents(): List<PhoneActivity> {
        if (sessionStartTimeMs == 0L) return emptyList()
        val endTime = System.currentTimeMillis()
        val usm = getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
        val events: UsageEvents = try { usm.queryEvents(sessionStartTimeMs, endTime) }
            catch (e: Exception) { Log.e(TAG, "查询 UsageEvents 失败: ${e.message}"); return emptyList() }
        val appMap = mutableMapOf<String, PhoneActivity>()
        var lastPkg: String? = null; var lastTime: Long = 0
        val event = UsageEvents.Event()
        while (events.hasNextEvent()) {
            events.getNextEvent(event)
            val pkg = event.packageName ?: continue
            if (pkg == packageName) continue
            when (event.eventType) {
                UsageEvents.Event.MOVE_TO_FOREGROUND -> { lastPkg = pkg; lastTime = event.timeStamp }
                UsageEvents.Event.ACTIVITY_PAUSED -> {
                    if (pkg == lastPkg && lastTime > 0) {
                        val existing = appMap[pkg]
                        if (existing == null) appMap[pkg] = PhoneActivity(
                            package_name = pkg, app_name = getAppName(pkg),
                            duration = (event.timeStamp - lastTime) / 1000.0 / 60.0,
                            first_seen = lastTime / 1000, last_seen = event.timeStamp / 1000, switch_count = 1)
                        else appMap[pkg] = existing.copy(
                            duration = existing.duration + (event.timeStamp - lastTime) / 1000.0 / 60.0,
                            last_seen = event.timeStamp / 1000, switch_count = existing.switch_count + 1)
                        lastPkg = null; lastTime = 0
                    }
                }
            }
        }
        if (lastPkg != null && lastTime > 0) {
            val existing = appMap[lastPkg]; val remaining = (endTime - lastTime) / 1000.0 / 60.0
            if (existing == null) appMap[lastPkg!!] = PhoneActivity(
                package_name = lastPkg!!, app_name = getAppName(lastPkg!!),
                duration = remaining, first_seen = lastTime / 1000,
                last_seen = endTime / 1000, switch_count = 1)
            else appMap[lastPkg!!] = existing.copy(duration = existing.duration + remaining, last_seen = endTime / 1000)
        }
        return appMap.values.sortedByDescending { it.duration }
    }

    private fun getAppName(packageName: String): String = try {
        val pm = packageManager; val ai = pm.getApplicationInfo(packageName, 0); pm.getApplicationLabel(ai).toString()
    } catch (e: Exception) { packageName }

    private fun toast(msg: String) { handler.post { Toast.makeText(this@UdpListenerService, msg, Toast.LENGTH_SHORT).show() } }
    private fun updateNotification(text: String) {
        (getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).notify(NOTIFICATION_ID, buildNotification(text))
    }
    private fun buildNotification(text: String): Notification {
        val pi = PendingIntent.getActivity(this, 0, Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        return Notification.Builder(this, CHANNEL_ID).setContentTitle("注意力番茄钟")
            .setContentText(text).setSmallIcon(android.R.drawable.ic_dialog_info).setContentIntent(pi).setOngoing(true).build()
    }
    private fun createNotificationChannel() {
        (getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager).createNotificationChannel(
            NotificationChannel(CHANNEL_ID, "专注会话监听", NotificationManager.IMPORTANCE_LOW).apply { description = "保持与电脑端的连接" })
    }
    private fun acquireWakeLock() {
        wakeLock = (getSystemService(Context.POWER_SERVICE) as PowerManager)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "AttentionPomodoro:Service").apply { acquire(10 * 60 * 1000L) }
    }
    override fun onBind(intent: Intent?): IBinder? = null
    override fun onDestroy() { polling = false; scope.cancel(); wakeLock?.release(); super.onDestroy() }
}
