package com.attention.app.data

import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

data class PhoneActivity(
    val package_name: String, val app_name: String, val duration: Double,
    val first_seen: Long, val last_seen: Long, val switch_count: Int
)

data class SessionReport(
    val session_id: String, val token: String, val activities: List<PhoneActivity>,
    val screen_unlocks: Int = 0, val total_monitored_sec: Long = 0
)

class ReportApi {
    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    suspend fun sendReport(ip: String, httpPort: Int, report: SessionReport): Result<String> =
        withContext(Dispatchers.IO) {
            try {
                val json = gson.toJson(report)
                val body = json.toRequestBody(jsonMediaType)
                val request = Request.Builder()
                    .url("http://$ip:$httpPort/report").post(body).build()
                val response = client.newCall(request).execute()
                if (response.isSuccessful) Result.success(response.body?.string() ?: "ok")
                else Result.failure(Exception("HTTP ${response.code}"))
            } catch (e: Exception) {
                Result.failure(e)
            }
        }

    suspend fun ping(ip: String, httpPort: Int): Boolean = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder().url("http://$ip:$httpPort/ping").get().build()
            client.newCall(request).execute().use { it.isSuccessful }
        } catch (e: Exception) { false }
    }

    suspend fun sendPairConfirm(ip: String, httpPort: Int, token: String, deviceName: String): Boolean =
        withContext(Dispatchers.IO) {
            try {
                val data = mapOf("token" to token, "device_name" to deviceName)
                val json = gson.toJson(data)
                val body = json.toRequestBody(jsonMediaType)
                val request = Request.Builder()
                    .url("http://$ip:$httpPort/pair_confirm").post(body).build()
                client.newCall(request).execute().use { it.isSuccessful }
            } catch (e: Exception) { false }
        }
}
