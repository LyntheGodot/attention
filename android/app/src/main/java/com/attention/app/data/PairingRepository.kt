package com.attention.app.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("pairing")

class PairingRepository(private val context: Context) {
    companion object {
        private val KEY_IP = stringPreferencesKey("pc_ip")
        private val KEY_UDP_PORT = stringPreferencesKey("udp_port")
        private val KEY_HTTP_PORT = stringPreferencesKey("http_port")
        private val KEY_TOKEN = stringPreferencesKey("token")
    }

    data class PairingInfo(
        val ip: String, val udpPort: Int, val httpPort: Int, val token: String
    ) {
        val isPaired: Boolean get() = ip.isNotEmpty() && token.isNotEmpty()
    }

    val pairingInfo: Flow<PairingInfo> = context.dataStore.data.map { prefs ->
        PairingInfo(
            ip = prefs[KEY_IP] ?: "",
            udpPort = (prefs[KEY_UDP_PORT] ?: "56789").toIntOrNull() ?: 56789,
            httpPort = (prefs[KEY_HTTP_PORT] ?: "56790").toIntOrNull() ?: 56790,
            token = prefs[KEY_TOKEN] ?: ""
        )
    }

    suspend fun savePairing(pcIp: String, udpPort: Int, httpPort: Int, token: String) {
        context.dataStore.edit {
            it[KEY_IP] = pcIp
            it[KEY_UDP_PORT] = udpPort.toString()
            it[KEY_HTTP_PORT] = httpPort.toString()
            it[KEY_TOKEN] = token
        }
    }

    suspend fun clearPairing() {
        context.dataStore.edit { it.clear() }
    }
}
