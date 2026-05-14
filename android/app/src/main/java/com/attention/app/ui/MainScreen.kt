package com.attention.app.ui

import android.content.Intent
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.attention.app.data.PairingRepository
import com.attention.app.data.ReportApi
import com.attention.app.service.UdpListenerService
import com.attention.app.service.UsageMonitorService
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(pairingRepo: PairingRepository, onNavigateToScan: () -> Unit, onNavigateToPermissions: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val pairingInfo by pairingRepo.pairingInfo.collectAsState(initial = null)
    val isMonitoring = UsageMonitorService.isMonitoring
    var showUnpairDialog by remember { mutableStateOf(false) }
    var showManualDialog by remember { mutableStateOf(false) }
    var manualJson by remember { mutableStateOf("") }

    Scaffold(topBar = { TopAppBar(title = { Text("注意力番茄钟", fontWeight = FontWeight.Bold) },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF3498DB), titleContentColor = Color.White)) }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(20.dp)) {
            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(
                containerColor = if (pairingInfo?.isPaired == true) Color(0xFFE8F5E9) else Color(0xFFFFF3E0))) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(imageVector = if (pairingInfo?.isPaired == true) Icons.Default.Phonelink else Icons.Default.PhonelinkOff,
                        contentDescription = null, tint = if (pairingInfo?.isPaired == true) Color(0xFF27AE60) else Color(0xFFE67E22),
                        modifier = Modifier.size(48.dp))
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = if (pairingInfo?.isPaired == true) "已配对" else "未配对", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                    if (pairingInfo?.isPaired == true) {
                        Text(text = "PC: ${pairingInfo!!.ip}", color = Color.Gray, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedButton(onClick = { showUnpairDialog = true },
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFFE74C3C))) { Text("取消配对") }
                    } else {
                        Spacer(modifier = Modifier.height(12.dp))
                        Button(onClick = onNavigateToScan) { Icon(Icons.Default.QrCodeScanner, contentDescription = null); Spacer(modifier = Modifier.width(8.dp)); Text("扫码配对") }
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedButton(onClick = { showManualDialog = true }) { Icon(Icons.Default.Edit, contentDescription = null); Spacer(modifier = Modifier.width(8.dp)); Text("手动输入配对") }
                    }
                }
            }
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(imageVector = if (isMonitoring) Icons.Default.Timer else Icons.Default.TimerOff,
                        contentDescription = null, tint = if (isMonitoring) Color(0xFF27AE60) else Color(0xFF95A5A6), modifier = Modifier.size(48.dp))
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = if (isMonitoring) "会话进行中" else "等待电脑端指令", fontSize = 16.sp, fontWeight = FontWeight.Medium)
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Button(onClick = { context.startForegroundService(Intent(context, UdpListenerService::class.java)) },
                    modifier = Modifier.weight(1f), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF3498DB))) { Text("启动监听") }
                OutlinedButton(onClick = { context.startService(Intent(context, UdpListenerService::class.java).apply { action = UdpListenerService.ACTION_STOP }) },
                    modifier = Modifier.weight(1f)) { Text("停止监听") }
            }
            OutlinedCard(modifier = Modifier.fillMaxWidth(), onClick = onNavigateToPermissions) {
                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Security, contentDescription = null, tint = Color(0xFFE67E22))
                    Spacer(modifier = Modifier.width(12.dp)); Text("权限检查与引导", fontWeight = FontWeight.Medium)
                    Spacer(modifier = Modifier.weight(1f)); Icon(Icons.Default.ChevronRight, contentDescription = null, tint = Color.Gray)
                }
            }
            Spacer(modifier = Modifier.weight(1f))
            Text(text = "请确保手机与电脑在同一 Wi-Fi 网络", color = Color.Gray, fontSize = 13.sp)
        }
        if (showUnpairDialog) AlertDialog(onDismissRequest = { showUnpairDialog = false }, title = { Text("确认取消配对") },
            text = { Text("取消配对后需要重新配对才能连接电脑端") },
            confirmButton = { TextButton(onClick = { scope.launch { pairingRepo.clearPairing() }; showUnpairDialog = false }) { Text("确认", color = Color(0xFFE74C3C)) } },
            dismissButton = { TextButton(onClick = { showUnpairDialog = false }) { Text("取消") } })
        if (showManualDialog) {
            AlertDialog(onDismissRequest = { showManualDialog = false }, title = { Text("手动输入配对信息") }, text = {
                Column {
                    Text(text = "粘贴 PC 端显示的配对 JSON：", fontSize = 13.sp, color = Color.Gray)
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(value = manualJson, onValueChange = { manualJson = it },
                        placeholder = { Text("{\"ip\":\"...\",\"token\":\"...\",...}") },
                        modifier = Modifier.fillMaxWidth().height(120.dp), maxLines = 5)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "模拟器: IP 改成 10.0.2.2\n真机: 使用 PC 的实际局域网 IP", fontSize = 12.sp, color = Color(0xFFE67E22))
                }
            }, confirmButton = {
                TextButton(onClick = {
                    try {
                        val gson = com.google.gson.Gson()
                        val map: Map<String, Any> = gson.fromJson(manualJson, Map::class.java) as Map<String, Any>
                        val ip = map["ip"] as? String ?: ""
                        val udpPort = (map["udp_port"] as? Double)?.toInt() ?: 56789
                        val httpPort = (map["http_port"] as? Double)?.toInt() ?: 56790
                        val token = map["token"] as? String ?: ""
                        if (ip.isNotEmpty() && token.isNotEmpty()) {
                            scope.launch { pairingRepo.savePairing(ip, udpPort, httpPort, token); ReportApi().sendPairConfirm(ip, httpPort, token, android.os.Build.MODEL) }
                            showManualDialog = false; manualJson = ""
                        }
                    } catch (_: Exception) {}
                }) { Text("确认配对") }
            }, dismissButton = { TextButton(onClick = { showManualDialog = false; manualJson = "" }) { Text("取消") } })
        }
    }
}
