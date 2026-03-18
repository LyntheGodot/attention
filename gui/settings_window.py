#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 设置界面
用于配置各种时间参数和声音设置
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsWindow(tk.Toplevel):
    """设置窗口"""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.title("设置")
        self.geometry("500x880")
        self.configure(bg="#ffffff")
        self.resizable(False, False)

        self.config = config.copy()
        self.on_save = None
        self.current_tab = "timer"  # 当前选项卡: timer 或 sound

        # 验证输入为数字
        vcmd = (self.register(self._validate_numeric), "%P")

        # 创建界面
        self._create_widgets(vcmd)

    def _validate_numeric(self, value):
        """验证输入是否为数字"""
        if value == "" or value.isdigit():
            return True
        return False

    def _create_widgets(self, vcmd):
        """创建界面组件"""
        # 标题栏
        title_frame = tk.Frame(self, bg="#ffffff")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            title_frame,
            text="设置",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(side="left")

        close_btn = tk.Button(
            title_frame,
            text="✕",
            command=self.destroy,
            font=("Arial", 18),
            bg="#ffffff",
            fg="#7f8c8d",
            relief="flat",
            width=2
        )
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg="#e74c3c"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg="#7f8c8d"))

        # 选项卡切换栏
        tab_frame = tk.Frame(self, bg="#ffffff")
        tab_frame.pack(fill="x", padx=20, pady=(0, 10))

        # 计时选项按钮
        self.timer_tab_btn = tk.Button(
            tab_frame,
            text="计时选项",
            font=("Microsoft YaHei UI", 12),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=20,
            pady=8,
            command=lambda: self._switch_tab("timer")
        )
        self.timer_tab_btn.pack(side="left", padx=(0, 5))

        # 声音选项按钮
        self.sound_tab_btn = tk.Button(
            tab_frame,
            text="声音",
            font=("Microsoft YaHei UI", 12),
            bg="#ecf0f1",
            fg="#7f8c8d",
            relief="flat",
            padx=20,
            pady=8,
            command=lambda: self._switch_tab("sound")
        )
        self.sound_tab_btn.pack(side="left")

        # 分隔线
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20)

        # 内容容器（用于切换不同设置页面）
        self.content_container = tk.Frame(self, bg="#ffffff")
        self.content_container.pack(fill="both", expand=True, padx=30, pady=20)

        # 创建两个页面的内容（只创建一次）
        self._create_timer_settings(vcmd)
        self._create_sound_settings()

        # 默认显示计时选项
        self._show_timer_settings()

        # 按钮区域（放在最底部，共享）
        self._create_button_area()

    def _create_timer_settings(self, vcmd):
        """创建计时选项页面的内容（不显示）"""
        self.timer_frame = tk.Frame(self.content_container, bg="#ffffff")

        # 专注时间
        focus_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        focus_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            focus_frame,
            text="专注时间:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.focus_entry = tk.Entry(
            focus_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.focus_entry.insert(0, str(self.config["focus_time"]))
        self.focus_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            focus_frame,
            text="分钟",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 最小间隔
        min_interval_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        min_interval_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            min_interval_frame,
            text="最小间隔:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.min_interval_entry = tk.Entry(
            min_interval_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.min_interval_entry.insert(0, str(self.config["min_interval"]))
        self.min_interval_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            min_interval_frame,
            text="分钟",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 最大间隔
        max_interval_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        max_interval_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            max_interval_frame,
            text="最大间隔:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.max_interval_entry = tk.Entry(
            max_interval_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.max_interval_entry.insert(0, str(self.config["max_interval"]))
        self.max_interval_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            max_interval_frame,
            text="分钟",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 微休息时间
        micro_break_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        micro_break_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            micro_break_frame,
            text="微休息时间:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.micro_break_entry = tk.Entry(
            micro_break_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.micro_break_entry.insert(0, str(self.config["micro_break"]))
        self.micro_break_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            micro_break_frame,
            text="秒",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 提示音次数
        alert_count_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        alert_count_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            alert_count_frame,
            text="提示音次数:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.alert_count_entry = tk.Entry(
            alert_count_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.alert_count_entry.insert(0, str(self.config.get("alert_count", 1)))
        self.alert_count_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            alert_count_frame,
            text="次",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 分隔线
        ttk.Separator(self.timer_frame, orient="horizontal").pack(fill="x", pady=20)

        # 休息时间
        break_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        break_frame.pack(fill="x", pady=(0, 15))
        tk.Label(
            break_frame,
            text="休息时间:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.break_entry = tk.Entry(
            break_frame,
            font=("Microsoft YaHei UI", 14),
            width=10,
            justify="center",
            validate="key",
            validatecommand=vcmd
        )
        self.break_entry.insert(0, str(self.config["break_time"]))
        self.break_entry.pack(side="left", padx=(20, 5))
        tk.Label(
            break_frame,
            text="分钟",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 休息倒计时开关
        break_countdown_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        break_countdown_frame.pack(fill="x", pady=(0, 20))
        tk.Label(
            break_countdown_frame,
            text="休息倒计时:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")
        self.break_countdown_var = tk.BooleanVar(value=self.config["break_countdown"])
        break_countdown_switch = tk.Checkbutton(
            break_countdown_frame,
            variable=self.break_countdown_var,
            bg="#ffffff",
            activebackground="#ffffff"
        )
        break_countdown_switch.pack(side="left", padx=(20, 0))

    def _create_sound_settings(self):
        """创建声音设置页面的内容（不显示）"""
        self.sound_frame = tk.Frame(self.content_container, bg="#ffffff")

        # 音量设置区域
        volume_section = tk.Frame(self.sound_frame, bg="#ffffff")
        volume_section.pack(fill="x", pady=(10, 0))

        # 音量图标和标题
        volume_title_frame = tk.Frame(volume_section, bg="#ffffff")
        volume_title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            volume_title_frame,
            text="🔊",
            font=("Segoe UI Emoji", 32),
            bg="#ffffff"
        ).pack(side="left", padx=(0, 15))

        tk.Label(
            volume_title_frame,
            text="提示音量",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(side="left")

        # 音量滑动条区域
        slider_frame = tk.Frame(volume_section, bg="#ffffff")
        slider_frame.pack(fill="x", pady=(10, 20))

        # 音量图标（小）
        tk.Label(
            slider_frame,
            text="🔈",
            font=("Segoe UI Emoji", 16),
            bg="#ffffff"
        ).pack(side="left", padx=(0, 10))

        # 自定义样式的滑动条
        self.volume_var = tk.DoubleVar(value=self.config.get("volume", 0.5) * 100)

        # 创建滑动条容器
        scale_container = tk.Frame(slider_frame, bg="#ffffff", height=40)
        scale_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 使用 ttk.Scale 并设置样式
        style = ttk.Style()
        style.configure(
            "Volume.Horizontal.TScale",
            background="#ffffff",
            troughcolor="#ecf0f1",
            sliderlength=30,
            sliderthickness=20
        )

        self.volume_scale = ttk.Scale(
            scale_container,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            style="Volume.Horizontal.TScale",
            command=self._on_volume_change
        )
        self.volume_scale.pack(fill="x", pady=10)

        # 音量百分比显示
        self.volume_label = tk.Label(
            slider_frame,
            text=f"{int(self.config.get('volume', 0.5) * 100)}%",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg="#ffffff",
            fg="#3498db",
            width=5
        )
        self.volume_label.pack(side="left")

        # 测试按钮
        test_frame = tk.Frame(self.sound_frame, bg="#ffffff")
        test_frame.pack(fill="x", pady=(30, 0))

        test_btn = tk.Button(
            test_frame,
            text="🔊 试听提示音",
            font=("Microsoft YaHei UI", 12),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=30,
            pady=12,
            command=self._test_sound
        )
        test_btn.pack(side="left")
        test_btn.bind("<Enter>", lambda e: test_btn.configure(bg="#2980b9"))
        test_btn.bind("<Leave>", lambda e: test_btn.configure(bg="#3498db"))

        # 提示文字
        tk.Label(
            self.sound_frame,
            text="调整音量后点击试听，可以测试当前音量效果",
            font=("Microsoft YaHei UI", 10),
            bg="#ffffff",
            fg="#7f8c8d"
        ).pack(side="left", padx=(20, 0))

        # 分隔线
        ttk.Separator(self.sound_frame, orient="horizontal").pack(fill="x", pady=40)

        # 白噪音设置区域
        white_noise_section = tk.Frame(self.sound_frame, bg="#ffffff")
        white_noise_section.pack(fill="x", pady=(0, 0))

        # 白噪音图标和标题
        white_noise_title_frame = tk.Frame(white_noise_section, bg="#ffffff")
        white_noise_title_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            white_noise_title_frame,
            text="🌲",
            font=("Segoe UI Emoji", 32),
            bg="#ffffff"
        ).pack(side="left", padx=(0, 15))

        tk.Label(
            white_noise_title_frame,
            text="白噪音音量",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).pack(side="left")

        # 白噪音类型选择
        type_frame = tk.Frame(white_noise_section, bg="#ffffff")
        type_frame.pack(fill="x", pady=(0, 20))

        tk.Label(
            type_frame,
            text="白噪音类型:",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        ).pack(side="left")

        # 白噪音类型下拉框 - 增加宽度
        self.white_noise_type_var = tk.StringVar(
            value="🌲 森林" if self.config.get("white_noise_type", "forest") == "forest" else "⛈️ 雷雨"
        )
        white_noise_type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.white_noise_type_var,
            values=["🌲 森林", "⛈️ 雷雨"],
            state="readonly",
            font=("Microsoft YaHei UI", 12),
            width=15
        )
        white_noise_type_combo.pack(side="left", padx=(20, 0))

        # 白噪音音量滑动条区域
        white_noise_slider_frame = tk.Frame(white_noise_section, bg="#ffffff")
        white_noise_slider_frame.pack(fill="x", pady=(10, 20))

        # 白噪音音量图标（小）
        tk.Label(
            white_noise_slider_frame,
            text="🔈",
            font=("Segoe UI Emoji", 16),
            bg="#ffffff"
        ).pack(side="left", padx=(0, 10))

        # 白噪音音量滑动条
        self.white_noise_volume_var = tk.DoubleVar(value=self.config.get("white_noise_volume", 0.5) * 100)

        # 创建滑动条容器
        white_noise_scale_container = tk.Frame(white_noise_slider_frame, bg="#ffffff", height=40)
        white_noise_scale_container.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.white_noise_volume_scale = ttk.Scale(
            white_noise_scale_container,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.white_noise_volume_var,
            style="Volume.Horizontal.TScale",
            command=self._on_white_noise_volume_change
        )
        self.white_noise_volume_scale.pack(fill="x", pady=10)

        # 白噪音音量百分比显示
        self.white_noise_volume_label = tk.Label(
            white_noise_slider_frame,
            text=f"{int(self.config.get('white_noise_volume', 0.5) * 100)}%",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg="#ffffff",
            fg="#27ae60",
            width=5
        )
        self.white_noise_volume_label.pack(side="left")

    def _create_button_area(self):
        """创建底部按钮区域"""
        button_frame = tk.Frame(self, bg="#ffffff")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))

        # 保存按钮
        save_btn = tk.Button(
            button_frame,
            text="保存",
            command=self._save_settings,
            font=("Microsoft YaHei UI", 14, "bold"),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=30,
            pady=10
        )
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg="#2980b9"))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg="#3498db"))

        # 重置按钮
        reset_btn = tk.Button(
            button_frame,
            text="重置",
            command=self._reset_settings,
            font=("Microsoft YaHei UI", 14),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            padx=30,
            pady=10
        )
        reset_btn.pack(side="left")
        reset_btn.bind("<Enter>", lambda e: reset_btn.configure(bg="#7f8c8d"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.configure(bg="#95a5a6"))

    def _switch_tab(self, tab_name):
        """切换选项卡"""
        self.current_tab = tab_name

        # 更新按钮样式
        if tab_name == "timer":
            self.timer_tab_btn.configure(bg="#3498db", fg="white")
            self.sound_tab_btn.configure(bg="#ecf0f1", fg="#7f8c8d")
            self._show_timer_settings()
        else:
            self.sound_tab_btn.configure(bg="#3498db", fg="white")
            self.timer_tab_btn.configure(bg="#ecf0f1", fg="#7f8c8d")
            self._show_sound_settings()

    def _show_timer_settings(self):
        """显示计时选项页面"""
        # 隐藏其他页面
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        # 显示当前页面
        self.timer_frame.pack(fill="both", expand=True)

    def _show_sound_settings(self):
        """显示声音设置页面"""
        # 隐藏其他页面
        for widget in self.content_container.winfo_children():
            widget.pack_forget()
        # 显示当前页面
        self.sound_frame.pack(fill="both", expand=True)

    def _on_volume_change(self, value):
        """音量滑动条变化时更新显示"""
        volume_pct = int(float(value))
        self.volume_label.configure(text=f"{volume_pct}%")

    def _on_white_noise_volume_change(self, value):
        """白噪音音量滑动条变化时更新显示"""
        volume_pct = int(float(value))
        self.white_noise_volume_label.configure(text=f"{volume_pct}%")

    def _test_sound(self):
        """测试播放提示音"""
        volume = self.volume_var.get() / 100.0
        try:
            # 从父窗口获取音频播放器
            if hasattr(self.parent, 'audio_player'):
                alert_count = 1
                if hasattr(self.parent, 'config_manager'):
                    config = self.parent.config_manager.get_all()
                    alert_count = config.get("alert_count", 1)
                self.parent.audio_player.play_notification(count=alert_count, volume=volume)
            else:
                # 尝试直接导入并创建
                from utils.audio import AudioPlayer
                audio = AudioPlayer()
                audio.play_notification(count=1, volume=volume)
        except Exception as e:
            print(f"播放测试音失败: {e}")

    def _save_settings(self):
        """保存设置"""
        try:
            # 保存音量设置
            self.config["volume"] = self.volume_var.get() / 100.0
            self.config["white_noise_volume"] = self.white_noise_volume_var.get() / 100.0

            # 保存白噪音类型
            type_text = self.white_noise_type_var.get()
            self.config["white_noise_type"] = "forest" if "森林" in type_text else "thunderstorm"

            # 如果在计时选项卡，保存计时设置
            if self.current_tab == "timer":
                focus_time = int(self.focus_entry.get() or "0")
                break_time = int(self.break_entry.get() or "0")
                min_interval = int(self.min_interval_entry.get() or "0")
                max_interval = int(self.max_interval_entry.get() or "0")
                micro_break = int(self.micro_break_entry.get() or "0")
                break_countdown = self.break_countdown_var.get()
                alert_count = int(self.alert_count_entry.get() or "1")

                # 验证输入
                if focus_time <= 0 or break_time <= 0:
                    raise ValueError("专注时间和休息时间必须大于0")
                if min_interval < 1:
                    raise ValueError("最小间隔至少为1分钟")
                if max_interval < min_interval:
                    raise ValueError("最大间隔必须大于等于最小间隔")
                if max_interval > focus_time:
                    raise ValueError(f"最大间隔不能超过专注时间 ({focus_time} 分钟)")
                if micro_break < 10:
                    raise ValueError("微休息时间至少为10秒")
                if alert_count < 1 or alert_count > 5:
                    raise ValueError("提示音次数必须在1-5次之间")

                self.config["focus_time"] = focus_time
                self.config["break_time"] = break_time
                self.config["min_interval"] = min_interval
                self.config["max_interval"] = max_interval
                self.config["micro_break"] = micro_break
                self.config["break_countdown"] = break_countdown
                self.config["alert_count"] = alert_count

            if self.on_save:
                self.on_save(self.config)

            messagebox.showinfo("成功", "设置已保存")
            self.destroy()

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {e}")

    def _reset_settings(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认", "确定要重置为默认设置吗？"):
            # 重置音量
            self.volume_var.set(50)
            self.volume_label.configure(text="50%")
            self.white_noise_volume_var.set(50)
            self.white_noise_volume_label.configure(text="50%")
            self.white_noise_type_var.set("🌲 森林")

            # 重置计时设置（先检查控件是否存在）
            if hasattr(self, 'focus_entry'):
                self.focus_entry.delete(0, tk.END)
                self.focus_entry.insert(0, "40")
            if hasattr(self, 'break_entry'):
                self.break_entry.delete(0, tk.END)
                self.break_entry.insert(0, "5")
            if hasattr(self, 'min_interval_entry'):
                self.min_interval_entry.delete(0, tk.END)
                self.min_interval_entry.insert(0, "5")
            if hasattr(self, 'max_interval_entry'):
                self.max_interval_entry.delete(0, tk.END)
                self.max_interval_entry.insert(0, "40")
            if hasattr(self, 'micro_break_entry'):
                self.micro_break_entry.delete(0, tk.END)
                self.micro_break_entry.insert(0, "60")
            if hasattr(self, 'break_countdown_var'):
                self.break_countdown_var.set(True)
            if hasattr(self, 'alert_count_entry'):
                self.alert_count_entry.delete(0, tk.END)
                self.alert_count_entry.insert(0, "1")
