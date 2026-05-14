package com.attention.app.data

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class UsageRepository {
    data class AppUsage(
        val packageName: String, val appName: String = "",
        val firstSeen: Long = System.currentTimeMillis(),
        var lastSeen: Long = System.currentTimeMillis(),
        var durationSec: Long = 0, var switchCount: Int = 1
    )

    private val _activities = MutableStateFlow<Map<String, AppUsage>>(emptyMap())
    val activities: StateFlow<Map<String, AppUsage>> = _activities.asStateFlow()
    private var screenUnlocks = 0
    private var sessionStartTime: Long = 0
    private var lastPackage: String = ""
    private var lastSwitchTime: Long = 0

    fun startSession() {
        _activities.value = emptyMap()
        screenUnlocks = 0
        sessionStartTime = System.currentTimeMillis()
        lastPackage = ""
        lastSwitchTime = 0
    }

    fun onAppSwitch(packageName: String, appName: String = "") {
        val now = System.currentTimeMillis()
        if (lastPackage.isNotEmpty() && lastSwitchTime > 0) {
            val elapsed = (now - lastSwitchTime) / 1000
            val current = _activities.value.toMutableMap()
            val entry = current[lastPackage] ?: AppUsage(packageName = lastPackage, appName = lastPackage, firstSeen = lastSwitchTime)
            entry.durationSec += elapsed
            entry.lastSeen = now
            current[lastPackage] = entry
            _activities.value = current
        }
        if (packageName != lastPackage) {
            val current = _activities.value.toMutableMap()
            val entry = current[packageName] ?: AppUsage(packageName = packageName, appName = appName.ifEmpty { packageName }, firstSeen = now)
            if (packageName in current) entry.switchCount++
            entry.lastSeen = now
            current[packageName] = entry
            _activities.value = current
        }
        lastPackage = packageName
        lastSwitchTime = now
    }

    fun onScreenUnlock() { screenUnlocks++ }

    fun getSessionDurationSec(): Long {
        if (sessionStartTime == 0L) return 0
        return (System.currentTimeMillis() - sessionStartTime) / 1000
    }

    fun buildReport(sessionId: String, token: String): SessionReport {
        val actList = _activities.value.values.filter { it.durationSec >= 1 }.map {
            PhoneActivity(
                package_name = it.packageName, app_name = it.appName,
                duration = it.durationSec / 60.0, first_seen = it.firstSeen / 1000,
                last_seen = it.lastSeen / 1000, switch_count = it.switchCount
            )
        }.sortedByDescending { it.duration }
        return SessionReport(session_id = sessionId, token = token, activities = actList,
            screen_unlocks = screenUnlocks, total_monitored_sec = getSessionDurationSec())
    }

    fun stopSession() {
        if (lastPackage.isNotEmpty() && lastSwitchTime > 0) onAppSwitch("")
    }
}
