package com.attention.app

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.attention.app.data.PairingRepository
import com.attention.app.service.UdpListenerService
import com.attention.app.ui.MainScreen
import com.attention.app.ui.PermissionGuideScreen
import com.attention.app.ui.ScanQRScreen

class MainActivity : ComponentActivity() {
    private lateinit var pairingRepo: PairingRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        pairingRepo = PairingRepository(this)
        startUdpListener()
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    val navController = rememberNavController()
                    NavHost(navController = navController, startDestination = "main") {
                        composable("main") {
                            MainScreen(pairingRepo = pairingRepo,
                                onNavigateToScan = { navController.navigate("scan") },
                                onNavigateToPermissions = { navController.navigate("permissions") })
                        }
                        composable("scan") {
                            ScanQRScreen(pairingRepo = pairingRepo,
                                onNavigateBack = { navController.popBackStack() })
                        }
                        composable("permissions") {
                            PermissionGuideScreen(onNavigateBack = { navController.popBackStack() })
                        }
                    }
                }
            }
        }
    }

    private fun startUdpListener() {
        startForegroundService(Intent(this, UdpListenerService::class.java))
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
    }
}
