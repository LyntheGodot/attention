package com.attention.app.ui

import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

data class PermissionItem(val name: String, val description: String, val isGranted: () -> Boolean, val action: (Context) -> Unit)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PermissionGuideScreen(onNavigateBack: () -> Unit) {
    val context = LocalContext.current
    val permissions = remember {
        listOf(
            PermissionItem(name = "使用情况访问", description = "用于记录手机 App 的前台使用时长。\n进入后找到「注意力番茄钟」并开启。",
                isGranted = {
                    try { (context.getSystemService(Context.APP_OPS_SERVICE) as android.app.AppOpsManager).checkOpNoThrow(android.app.AppOpsManager.OPSTR_GET_USAGE_STATS, android.os.Process.myUid(), context.packageName) == android.app.AppOpsManager.MODE_ALLOWED }
                    catch (e: Exception) { false }
                },
                action = { ctx -> ctx.startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)) }),
            PermissionItem(name = "无障碍服务", description = "实时监测前台 App 切换。\n进入「无障碍 → 已安装的应用」找到本 App 并开启。",
                isGranted = { (Settings.Secure.getString(context.contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: "").contains(context.packageName) },
                action = { ctx -> ctx.startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)) }),
            PermissionItem(name = "通知权限", description = "用于显示前台服务通知（Android 13+ 必须）。",
                isGranted = { if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) context.checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) == android.content.pm.PackageManager.PERMISSION_GRANTED else true },
                action = { ctx -> if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) { val i = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS); i.data = Uri.fromParts("package", ctx.packageName, null); ctx.startActivity(i) } }),
            PermissionItem(name = "忽略电池优化", description = "防止后台被系统杀掉。",
                isGranted = { (context.getSystemService(Context.POWER_SERVICE) as android.os.PowerManager).isIgnoringBatteryOptimizations(context.packageName) },
                action = { ctx -> val i = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS); i.data = Uri.parse("package:${ctx.packageName}"); ctx.startActivity(i) })
        )
    }

    Scaffold(topBar = { TopAppBar(title = { Text("权限检查") },
        navigationIcon = { IconButton(onClick = onNavigateBack) { Icon(Icons.Default.ArrowBack, "返回", tint = Color.White) } },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF3498DB), titleContentColor = Color.White)) }
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(text = "以下权限用于记录手机 App 使用情况，请在设置中手动开启：", color = Color.Gray, fontSize = 14.sp)
            permissions.forEach { perm ->
                val granted = perm.isGranted()
                Card(modifier = Modifier.fillMaxWidth().clickable { perm.action(context) }) {
                    Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(imageVector = if (granted) Icons.Default.CheckCircle else Icons.Default.Warning,
                            contentDescription = null, tint = if (granted) Color(0xFF27AE60) else Color(0xFFE67E22), modifier = Modifier.size(28.dp))
                        Spacer(modifier = Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(text = perm.name, fontWeight = FontWeight.Medium, fontSize = 16.sp, color = if (granted) Color(0xFF27AE60) else Color.Unspecified)
                            Text(text = perm.description, fontSize = 13.sp, color = Color.Gray)
                        }
                    }
                }
            }
        }
    }
}
