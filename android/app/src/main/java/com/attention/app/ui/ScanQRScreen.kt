package com.attention.app.ui

import android.Manifest
import android.content.pm.PackageManager
import android.util.Size
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.attention.app.data.PairingRepository
import com.attention.app.data.ReportApi
import com.google.gson.Gson
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import kotlinx.coroutines.launch
import java.util.concurrent.Executors

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScanQRScreen(pairingRepo: PairingRepository, onNavigateBack: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val lifecycleOwner = LocalLifecycleOwner.current
    var statusText by remember { mutableStateOf("将二维码对准取景框") }
    var processed by remember { mutableStateOf(false) }
    var statusColor by remember { mutableStateOf(Color.White) }
    var hasCameraPermission by remember { mutableStateOf(ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { hasCameraPermission = it }
    LaunchedEffect(Unit) { if (!hasCameraPermission) cameraPermissionLauncher.launch(Manifest.permission.CAMERA) }

    Scaffold(topBar = { TopAppBar(title = { Text("扫码配对") },
        navigationIcon = { IconButton(onClick = onNavigateBack) { Icon(Icons.Default.ArrowBack, "返回", tint = Color.White) } },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF3498DB), titleContentColor = Color.White)) }
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            if (hasCameraPermission) {
                AndroidView(factory = { ctx ->
                    val previewView = PreviewView(ctx)
                    val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                    cameraProviderFuture.addListener({
                        val cameraProvider = cameraProviderFuture.get()
                        val preview = Preview.Builder().build().also { it.setSurfaceProvider(previewView.surfaceProvider) }
                        val analyzer = ImageAnalysis.Builder().setTargetResolution(Size(1280, 720)).setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST).build()
                            .also { analysis -> analysis.setAnalyzer(Executors.newSingleThreadExecutor()) { imageProxy ->
                                val mediaImage = imageProxy.image
                                if (mediaImage != null) {
                                    val inputImage = InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
                                    BarcodeScanning.getClient().process(inputImage)
                                        .addOnSuccessListener { barcodes ->
                                            if (!processed) {
                                                for (barcode in barcodes) {
                                                    val rawValue = barcode.rawValue ?: continue
                                                    if (barcode.valueType == Barcode.TYPE_TEXT) {
                                                        processed = true
                                                        handleQRCode(rawValue, pairingRepo, scope, onNavigateBack) { text, color -> statusText = text; statusColor = color }
                                                    }
                                                }
                                            }
                                        }.addOnCompleteListener { imageProxy.close() }
                                }
                            } }
                        try { cameraProvider.unbindAll(); cameraProvider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, preview, analyzer) }
                        catch (e: Exception) { statusText = "相机启动失败: ${e.message}"; statusColor = Color(0xFFE74C3C) }
                    }, ContextCompat.getMainExecutor(ctx))
                    previewView }, modifier = Modifier.fillMaxSize())
                Surface(modifier = Modifier.fillMaxWidth().align(Alignment.BottomCenter).padding(bottom = 60.dp, start = 24.dp, end = 24.dp),
                    color = statusColor.copy(alpha = 0.85f), shape = MaterialTheme.shapes.medium) {
                    Text(text = statusText, color = Color.White, fontSize = 16.sp, modifier = Modifier.padding(16.dp))
                }
            } else {
                Column(modifier = Modifier.align(Alignment.Center), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text("需要相机权限才能扫码", fontSize = 16.sp); Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = { cameraPermissionLauncher.launch(Manifest.permission.CAMERA) }) { Text("授予权限") }
                }
            }
        }
    }
}

private fun handleQRCode(rawValue: String, pairingRepo: PairingRepository, scope: kotlinx.coroutines.CoroutineScope, onNavigateBack: () -> Unit, onStatus: (String, Color) -> Unit) {
    try {
        val gson = Gson(); val data = gson.fromJson(rawValue, Map::class.java)
        val ip = data["ip"] as? String ?: throw Exception("缺少 IP")
        val udpPort = (data["udp_port"] as? Double)?.toInt() ?: 56789
        val httpPort = (data["http_port"] as? Double)?.toInt() ?: 56790
        val token = data["token"] as? String ?: throw Exception("缺少 Token")
        scope.launch {
            pairingRepo.savePairing(ip, udpPort, httpPort, token)
            ReportApi().sendPairConfirm(ip, httpPort, token, android.os.Build.MODEL)
            onStatus("配对成功！IP: $ip", Color(0xFF27AE60)); kotlinx.coroutines.delay(1500); onNavigateBack()
        }
    } catch (e: Exception) { onStatus("无效的二维码: ${e.message}", Color(0xFFE74C3C)) }
}
