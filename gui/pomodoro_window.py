#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 番茄钟界面
包含可视化进度圆环和控制功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from PIL import Image, ImageTk
from gui.settings_window import SettingsWindow
from utils.timer import PomodoroTimer, TimerState
from utils.audio import AudioPlayer
from utils.config import ConfigManager
from utils.stats import StatsManager
from utils.window_monitor import WindowMonitor
from utils.activity_storage import ActivityStorageManager
from utils.distraction_blacklist import DistractionBlacklist
from gui.toast import Toast


class PomodoroWindow(tk.Toplevel):
    """番茄钟界面窗口"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("随机番茄钟")
        self.geometry("600x750")  # 增大窗口高度
        self.configure(bg="#ffffff")
        self.resizable(False, False)

        self.config_manager = ConfigManager()
        self.audio_player = AudioPlayer()

        # 初始化计时器
        config = self.config_manager.get_all()
        self.timer = PomodoroTimer(
            focus_time=config["focus_time"],
            break_time=config["break_time"],
            min_interval=config["min_interval"],
            max_interval=config["max_interval"],
            micro_break=config["micro_break"]
        )

        self.timer.on_tick = self._on_timer_tick
        self.timer.on_complete = self._on_timer_complete
        self.timer.on_random_alert = self._on_random_alert
        self.timer.on_micro_break_start = self._on_micro_break_start
        self.timer.on_micro_break_end = self._on_micro_break_end

        self.is_micro_break = False
        self.white_noise_playing = False
        self.white_noise_paused = False

        # 窗口监测和活动存储
        self.window_monitor = WindowMonitor()
        self.activity_storage = ActivityStorageManager()
        self.distraction_blacklist = DistractionBlacklist()

        # 设置分心检测回调
        self.window_monitor.distraction_checker = self.distraction_blacklist.matches
        self.window_monitor.on_distraction = self._on_distraction_detected

        # 创建界面
        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部栏
        top_frame = tk.Frame(self, bg="#f8f9fa", height=60)
        top_frame.pack(fill="x", padx=20, pady=(10, 5))  # 减少顶部和中间间距
        top_frame.pack_propagate(False)

        # 返回按钮
        back_btn = tk.Button(
            top_frame,
            text="返回",
            command=self._go_back,
            font=("Microsoft YaHei UI", 12),
            bg="#f8f9fa",
            fg="#7f8c8d",
            relief="flat",
            padx=10
        )
        back_btn.pack(side="left")
        back_btn.bind("<Enter>", lambda e: back_btn.configure(bg="#e0e0e0"))
        back_btn.bind("<Leave>", lambda e: back_btn.configure(bg="#f8f9fa"))

        # 设置按钮
        settings_btn = tk.Button(
            top_frame,
            text="⚙",
            command=self._open_settings,
            font=("Arial", 24),
            bg="#f8f9fa",
            fg="#34495e",
            relief="flat",
            width=3,
            height=1
        )
        settings_btn.pack(side="right")
        settings_btn.bind("<Enter>", lambda e: settings_btn.configure(bg="#e0e0e0"))
        settings_btn.bind("<Leave>", lambda e: settings_btn.configure(bg="#f8f9fa"))

        # 计时器显示区域
        timer_frame = tk.Frame(self, bg="#ffffff")
        timer_frame.pack(fill="both", expand=True, padx=40, pady=(5, 10))  # 减少间距

        # 进度圆环
        self.canvas = tk.Canvas(timer_frame, width=400, height=400, bg="#ffffff", highlightthickness=0)  # 增大画布
        self.canvas.pack(pady=(0, 10))  # 减少间距

        # 圆环参数
        self.circle_radius = 160
        self.circle_center = 200
        self.circle_width = 12
        self.circle_bg = "#e0e0e0"
        self.circle_fg = "#3498db"

        # 绘制背景圆环
        self._draw_background_circle()

        # 初始化时绘制时间
        self.update_time_label()

        # 状态提示
        self.status_label = tk.Label(
            timer_frame,
            text="准备开始",
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=5)  # 减少间距

        # 控制按钮
        control_frame = tk.Frame(timer_frame, bg="#ffffff")
        control_frame.pack(pady=(10, 0), fill="x")  # 调整间距

        self.start_btn = tk.Button(
            control_frame,
            text="开始",
            command=self._toggle_timer,
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#ffffff",
            fg="#3498db",
            relief="flat",
            padx=80,
            pady=18,
            borderwidth=2,
            highlightbackground="#3498db",
            highlightcolor="#3498db"
        )
        self.start_btn.pack(pady=(0, 10))

        self.reset_btn = tk.Button(
            control_frame,
            text="重置",
            command=self._reset_timer,
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#7f8c8d",
            relief="flat",
            padx=40,
            pady=12
        )
        self.reset_btn.pack()

        # 白噪音按钮
        self.white_noise_btn = tk.Button(
            control_frame,
            text="🌲 播放白噪音",
            command=self._toggle_white_noise,
            font=("Microsoft YaHei UI", 12),
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=30,
            pady=10,
            state="disabled"
        )
        self.white_noise_btn.pack(pady=(15, 0))
        self.white_noise_btn.bind("<Enter>", lambda e: self.white_noise_btn.configure(bg="#219a52"))
        self.white_noise_btn.bind("<Leave>", lambda e: self.white_noise_btn.configure(bg="#27ae60"))

        # 绑定按钮悬停效果
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.configure(bg="#2980b9"))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.configure(bg="#3498db"))
        self.reset_btn.bind("<Enter>", lambda e: self.reset_btn.configure(bg="#7f8c8d"))
        self.reset_btn.bind("<Leave>", lambda e: self.reset_btn.configure(bg="#95a5a6"))

        # 调整控件布局
        self.update_time_label()

    def _draw_background_circle(self):
        """绘制背景圆环"""
        self.canvas.create_oval(
            self.circle_center - self.circle_radius,
            self.circle_center - self.circle_radius,
            self.circle_center + self.circle_radius,
            self.circle_center + self.circle_radius,
            outline=self.circle_bg,
            width=self.circle_width
        )

    def _draw_progress_circle(self, progress):
        """绘制进度圆环"""
        # 清除现有进度圆弧
        self.canvas.delete("progress")

        # 计算弧度
        start_angle = -90  # 顶部为0度
        end_angle = start_angle + (360 * progress)

        # 绘制进度圆弧
        self.canvas.create_arc(
            self.circle_center - self.circle_radius,
            self.circle_center - self.circle_radius,
            self.circle_center + self.circle_radius,
            self.circle_center + self.circle_radius,
            start=start_angle,
            extent=end_angle - start_angle,
            outline=self.circle_fg,
            width=self.circle_width,
            tags="progress",
            style="arc"
        )

    def update_time_label(self):
        """更新时间标签"""
        time_text = self.timer.get_remaining_text()

        # 清除之前的时间文本
        self.canvas.delete("time_text")

        # 在圆环内部绘制时间
        self.canvas.create_text(
            self.circle_center,
            self.circle_center,
            text=time_text,
            font=("Microsoft YaHei UI", 56, "bold"),
            fill="#2c3e50",
            tags="time_text"
        )

        # 更新进度圆环
        progress = self.timer.get_progress()
        self._draw_progress_circle(progress)

    def _toggle_timer(self):
        """切换计时器状态"""
        if self.timer.state == TimerState.IDLE:
            self.timer.start()
            self.start_btn.config(text="暂停")
            self.start_btn.config(fg="#e74c3c")
            self.start_btn.config(highlightbackground="#e74c3c")
            self.status_label.config(text="专注进行中")
            # 启用白噪音按钮
            self.white_noise_btn.config(state="normal")
            # 启动窗口监测
            self.window_monitor._distraction_cooldown.clear()
            self.window_monitor.start()
        elif self.timer.state == TimerState.RUNNING:
            self.timer.pause()
            self.start_btn.config(text="继续")
            self.start_btn.config(fg="#27ae60")
            self.start_btn.config(highlightbackground="#27ae60")
            self.status_label.config(text="已暂停")
            # 暂停窗口监测
            self.window_monitor.pause()
        elif self.timer.state == TimerState.PAUSED:
            self.timer.start()
            self.start_btn.config(text="暂停")
            self.start_btn.config(fg="#e74c3c")
            self.start_btn.config(highlightbackground="#e74c3c")
            self.status_label.config(text="专注进行中")
            # 恢复窗口监测
            self.window_monitor.resume()

    def _toggle_white_noise(self):
        """切换白噪音播放状态"""
        config = self.config_manager.get_all()
        volume = config.get("white_noise_volume", 0.5)
        noise_type = config.get("white_noise_type", "forest")

        if not self.white_noise_playing:
            # 开始播放
            if self.audio_player.play_white_noise(volume=volume, noise_type=noise_type):
                self.white_noise_playing = True
                self.white_noise_paused = False
                self.white_noise_btn.config(text="🌲 暂停白噪音")
        else:
            if self.white_noise_paused:
                # 继续播放
                self.audio_player.unpause_white_noise()
                self.white_noise_paused = False
                self.white_noise_btn.config(text="🌲 暂停白噪音")
            else:
                # 暂停播放
                self.audio_player.pause_white_noise()
                self.white_noise_paused = True
                self.white_noise_btn.config(text="🌲 继续白噪音")

    def _reset_timer(self):
        """重置计时器"""
        # 停止窗口监测
        if self.window_monitor.is_running():
            self.window_monitor.stop()

        self.timer.reset()
        self.start_btn.config(text="开始")
        self.start_btn.config(fg="#3498db")
        self.start_btn.config(highlightbackground="#3498db")
        self.status_label.config(text="准备开始")
        self.is_micro_break = False
        # 停止白噪音并禁用按钮
        self._stop_white_noise()
        self.white_noise_btn.config(state="disabled")
        self.update_time_label()

    def _stop_white_noise(self):
        """停止白噪音并重置状态"""
        if self.white_noise_playing:
            self.audio_player.stop_white_noise()
            self.white_noise_playing = False
            self.white_noise_paused = False
            self.white_noise_btn.config(text="🌲 播放白噪音")

    def _go_back(self):
        """返回主菜单"""
        # 停止窗口监测
        if self.window_monitor.is_running():
            self.window_monitor.stop()

        self.timer.reset()
        self._stop_white_noise()
        self._cleanup()
        if hasattr(self, 'parent'):
            self.parent.deiconify()
        self.destroy()

    def _open_settings(self):
        """打开设置窗口"""
        settings_window = SettingsWindow(self, self.config_manager.get_all())
        settings_window.on_save = self._on_settings_save
        settings_window.mainloop()

    def _on_settings_save(self, config):
        """设置保存事件"""
        for key, value in config.items():
            self.config_manager.set(key, value)
        self.config_manager.save_config()
        self.timer.set_times(
            focus_time=config["focus_time"],
            break_time=config["break_time"],
            min_interval=config["min_interval"],
            max_interval=config["max_interval"],
            micro_break=config["micro_break"]
        )
        self.update_time_label()
        self._reset_timer()

    def _on_timer_tick(self, remaining, total, is_micro_break=False):
        """计时器滴答事件"""
        if is_micro_break:
            # 微休息期间更新
            time_text = f"{int(remaining)}秒"
            self.canvas.delete("time_text")
            self.canvas.create_text(
                self.circle_center,
                self.circle_center,
                text=time_text,
                font=("Microsoft YaHei UI", 40, "bold"),
                fill="#2c3e50",
                tags="time_text"
            )
            progress = (total - remaining) / total
            self._draw_progress_circle(progress)
        else:
            # 正常计时更新
            self.update_time_label()

    def _on_timer_complete(self):
        """计时完成事件"""
        config = self.config_manager.get_all()
        volume = config.get("volume", 0.5)
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=volume)
        messagebox.showinfo("完成", "专注时间结束！")

        # 记录专注时间
        stats_manager = StatsManager()
        stats_manager.add_focus_time(stats_manager.get_today_str(), config["focus_time"])

        # 停止窗口监测并获取活动记录
        activities = self.window_monitor.stop() if self.window_monitor.is_running() else []

        # 重置计时器
        self._reset_timer()

        # 如果有活动记录，弹出评估窗口
        if activities:
            try:
                from gui.self_assessment_window import SelfAssessmentWindow
                assessment_window = SelfAssessmentWindow(self, activities, config["focus_time"])
                assessment_window.on_save = self._on_assessment_save
                assessment_window.mainloop()
            except Exception as e:
                print(f"打开评估窗口失败: {e}")
                import traceback
                traceback.print_exc()

    def _on_assessment_save(self, activities):
        """保存评估结果"""
        try:
            config = self.config_manager.get_all()
            self.activity_storage.add_session_record(activities, config["focus_time"])
            # 重新加载黑名单（用户刚才标注了新的分心行为）
            self.distraction_blacklist.reload()
        except Exception as e:
            print(f"保存活动记录失败: {e}")
            import traceback
            traceback.print_exc()

    def _on_distraction_detected(self, app_name: str, domain: str, window_title: str):
        """分心窗口检测回调（来自 WindowMonitor 的后台线程）"""
        if domain:
            msg = f"⚠ 你曾标记过 '{domain}' 是分心来源\n注意收回你的注意力哦 ~"
        else:
            msg = f"⚠ 你曾标记过 '{app_name}' 是分心来源\n注意收回你的注意力哦 ~"

        # 在 tkinter 主线程中创建 Toast
        try:
            self.after(0, lambda: Toast.show(self, msg, is_warning=True))
        except tk.TclError:
            pass

    def _on_random_alert(self):
        """随机提示事件"""
        config = self.config_manager.get_all()
        volume = config.get("volume", 0.5)
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=volume)

    def _on_micro_break_start(self):
        """微休息开始事件"""
        self.is_micro_break = True
        self.configure(bg="#e8f5e9")
        self._update_all_widgets_bg("#e8f5e9")
        # 暂停窗口监测，微休息时间不记录
        self.window_monitor.pause()

        # 更新圆环内的时间显示
        self.canvas.delete("time_text")
        self.canvas.create_text(
            self.circle_center,
            self.circle_center,
            text=f"{self.timer.micro_break}秒",
            font=("Microsoft YaHei UI", 40, "bold"),
            fill="#2c3e50",
            tags="time_text"
        )
        self.status_label.config(text="现在，收回你的注意力，闭上眼睛去感知它")

    def _on_micro_break_end(self):
        """微休息结束事件"""
        self.is_micro_break = False
        self.configure(bg="#ffffff")
        self._update_all_widgets_bg("#ffffff")
        # 恢复窗口监测
        self.window_monitor.resume()

        config = self.config_manager.get_all()
        volume = config.get("volume", 0.5)
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=volume)
        self.update_time_label()
        self.status_label.config(text="专注进行中")

    def _update_all_widgets_bg(self, color):
        """更新所有控件的背景色"""
        for widget in self.winfo_children():
            self._update_widget_bg(widget, color)

    def _update_widget_bg(self, widget, color):
        """递归更新控件背景色"""
        if hasattr(widget, "configure") and widget != self.canvas:
            try:
                widget.configure(bg=color)
            except:
                pass
        for child in widget.winfo_children():
            self._update_widget_bg(child, color)

    def _cleanup(self):
        """清理资源"""
        self.timer.reset()
        self.audio_player.cleanup()

    def destroy(self):
        """销毁窗口时清理资源"""
        self._cleanup()
        super().destroy()
