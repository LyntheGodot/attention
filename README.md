# 注意力番茄钟 · Attention is all you need!

> 一款专为专注力低下、ADHD人群打造的随机番茄钟应用。**PC + Android 双端协同**，利用心理学效应让专注变得轻松有趣。

---

## 📥 下载安装

| 平台 | 文件 | 说明 |
|------|------|------|
| 🖥️ **Windows 电脑** | [attention.exe](https://github.com/LyntheGodot/attention/releases/latest/download/attention.exe) | 绿色免安装，双击运行 |
| 📱 **Android 手机** | [app-debug.apk](https://github.com/LyntheGodot/attention/releases/latest/download/app-debug.apk) | 传输到手机后点击安装 |

> 💡 **推荐双端搭配使用**：电脑专注 + 手机监测，互相监督效果最佳。

---

## 🚀 快速开始

### 🖥️ PC 端

1. 下载 `attention.exe`，双击运行
2. 点击「**随机番茄钟**」进入专注界面
3. 点击右上角 **⚙️** 自定义参数（时长、间隔、提示音等）
4. 点击「**开始**」进入专注，听到提示音时短暂闭眼收回注意力
5. 专注完成后在「**统计**」页面查看趋势

### 📱 Android 端

1. 下载 `app-debug.apk` 安装到手机，打开 App
2. 点击「**权限检查与引导**」→ 逐项开启所需权限（使用情况访问、通知等）
3. 点击「**启动监听**」，手机进入待命状态

### 🔗 双端配对

1. PC 端进入番茄钟界面 → 点 **📱 配对手机**
2. 手机端点「**扫码配对**」扫 PC 屏幕上的二维码（或点「手动输入配对」粘贴 JSON）
3. 配对成功后，PC 端点「开始」专注 → 手机自动开始监测 App 使用情况
4. 专注结束 → 手机自动上报数据 → PC 端评估窗口展示手机使用记录

> ⚠️ **网络要求**：PC 和手机需在同一局域网（连同一 WiFi 或用手机热点）

---

## ✨ 功能一览

### PC 端
- 🍅 **可视化进度**：优雅的进度圆环实时显示专注进度
- 🔔 **随机提示**：可变比率强化，随机时间点提醒收回注意力（可设为 0 = 纯净模式）
- 🌿 **微休息**：浅绿色界面引导短暂正念休息
- 🌲 **白噪音**：森林/雷雨两种白噪音，独立音量调节
- 📈 **专注统计**：14 天柱状图趋势 + 每次会话的窗口活动详情
- 🧠 **分心检测**：自动记录前台窗口，专注结束后人工标注分心行为，形成分心黑名单实时提醒
- ⚙️ **灵活配置**：专注时长、休息时长、随机间隔、微休息时长、提示音次数(0~5)、白噪音类型

### Android 端
- 📊 **App 使用监测**：自动记录专注期间的手机 App 前台使用情况
- 🔄 **HTTP 轮询**：每 2 秒检测 PC 端会话状态，自动启动/停止监测
- 📤 **自动上报**：专注结束后汇总数据回传 PC
- 📱 **QR 扫码配对**：扫 PC 端二维码完成配对，或手动输入 JSON
- 🔐 **权限引导**：一站式引导开启所需系统权限

### 双端协同
- PC 开始专注 → 手机自动启动监测
- PC 结束专注 → 手机停止监测并回传数据
- 手机 App 使用记录合并到 PC 评估窗口，统一标注分心行为

---

## ⚙️ 设置说明

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| 专注时间 | 40 分钟 | 单次专注时长 |
| 休息时间 | 5 分钟 | 专注结束后的休息时长 |
| 最小间隔 | 5 分钟 | 两次随机提示的最小间隔 |
| 最大间隔 | 40 分钟 | 两次随机提示的最大间隔 |
| 微休息时间 | 60 秒 | 随机提示后的短暂休息 |
| 提示音次数 | 1 次 | **设为 0 即纯净模式**，中途无打扰 |
| 白噪音类型 | 森林 | 可选森林 / 雷雨 |

---

## 🛠️ 开发者

### PC 端

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python main.py

# 打包为 exe
pyinstaller --clean 注意力番茄钟.spec
```

### Android 端

```bash
cd android
./gradlew assembleDebug
# APK 位于 app/build/outputs/apk/debug/app-debug.apk
```

依赖：JDK 17 + Android SDK (API 34)

---

## 📁 项目结构

```
attention/
├── main.py                     # PC 端入口
├── requirements.txt            # Python 依赖
├── 注意力番茄钟.spec           # PyInstaller 配置
├── lingsheng/                  # 音频资源
├── gui/                        # PC 端界面
│   ├── main_window.py          # 主菜单
│   ├── pomodoro_window.py      # 番茄钟核心界面
│   ├── settings_window.py      # 设置
│   ├── stats_window.py         # 统计
│   ├── self_assessment_window.py  # 分心标注
│   ├── phone_pairing_window.py # 手机配对
│   └── toast.py                # Toast 浮层
├── utils/                      # PC 端工具模块
│   ├── timer.py                # 计时器
│   ├── audio.py                # 音频
│   ├── config.py               # 配置管理
│   ├── stats.py                # 统计
│   ├── window_monitor.py       # 窗口监测
│   ├── activity_storage.py     # 活动存储
│   ├── category_mapper.py      # 分类映射
│   ├── distraction_blacklist.py # 分心黑名单
│   ├── network_pairing.py      # 配对管理
│   ├── udp_broadcaster.py      # UDP 广播
│   └── http_receiver.py        # HTTP 接收
└── android/                    # Android 端
    └── app/src/main/java/com/attention/app/
        ├── MainActivity.kt           # 入口
        ├── data/                     # 数据层
        │   ├── PairingRepository.kt  # 配对存储
        │   ├── ReportApi.kt          # HTTP 上报
        │   └── UsageRepository.kt    # 使用记录
        ├── service/
        │   ├── UdpListenerService.kt # HTTP 轮询服务
        │   └── UsageMonitorService.kt # 无障碍监测
        └── ui/                       # Compose 界面
            ├── MainScreen.kt         # 主屏幕
            ├── ScanQRScreen.kt       # 扫码
            └── PermissionGuideScreen.kt # 权限引导
```

---

## 🧠 设计理念

1. **可变比率强化**：随机时间的提示音比固定间隔更能强化专注行为
2. **正念冥想**：微休息时间引导注意力回收，提升元认知能力
3. **最小摩擦力**：简洁界面，降低启动专注的心理门槛
4. **正向反馈循环**：数据统计让进步可视化，增强自我效能感
5. **双端协同**：PC 工作 + 手机监测，覆盖注意力流失的全场景

---

## 📄 许可证

MIT License

---

"Attention is all you need!" — 专注于当下，感知自我。
