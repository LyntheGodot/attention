#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 番茄钟界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import uuid
from PIL import Image, ImageTk
from gui.settings_window import SettingsWindow
from gui.phone_pairing_window import PhonePairingWindow
from utils.timer import PomodoroTimer, TimerState
from utils.audio import AudioPlayer
from utils.config import ConfigManager
from utils.stats import StatsManager
from utils.window_monitor import WindowMonitor
from utils.activity_storage import ActivityStorageManager
from utils.distraction_blacklist import DistractionBlacklist
from utils.network_pairing import PairingManager
from utils.udp_broadcaster import UdpBroadcaster
from utils.http_receiver import HttpReceiver
from gui.toast import Toast


class PomodoroWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("随机番茄钟")
        self.geometry("600x750")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        self.config_manager = ConfigManager()
        self.audio_player = AudioPlayer()
        config = self.config_manager.get_all()
        self.timer = PomodoroTimer(
            focus_time=config["focus_time"], break_time=config["break_time"],
            min_interval=config["min_interval"], max_interval=config["max_interval"],
            micro_break=config["micro_break"], alert_count=config.get("alert_count", 1)
        )
        self.timer.on_tick = self._on_timer_tick
        self.timer.on_complete = self._on_timer_complete
        self.timer.on_random_alert = self._on_random_alert
        self.timer.on_micro_break_start = self._on_micro_break_start
        self.timer.on_micro_break_end = self._on_micro_break_end
        self.is_micro_break = False
        self.white_noise_playing = False
        self.white_noise_paused = False
        self.window_monitor = WindowMonitor()
        self.activity_storage = ActivityStorageManager()
        self.distraction_blacklist = DistractionBlacklist()
        self.window_monitor.distraction_checker = self.distraction_blacklist.matches
        self.window_monitor.on_distraction = self._on_distraction_detected
        self.pairing_manager = PairingManager()
        config = self.config_manager.get_all()
        udp_port = config.get("phone_udp_port", 56789)
        http_port = config.get("phone_http_port", 56790)
        self.udp_broadcaster = UdpBroadcaster(port=udp_port)
        self.http_receiver = HttpReceiver(port=http_port)
        self.http_receiver.on_report = self._on_phone_report
        self.http_receiver.on_pair_confirm = self._on_pair_confirm
        self._session_id: str = ""
        self._phone_reports: list = []
        self._create_widgets()

    def _create_widgets(self):
        top_frame = tk.Frame(self, bg="#f8f9fa", height=60)
        top_frame.pack(fill="x", padx=20, pady=(10, 5))
        top_frame.pack_propagate(False)
        back_btn = tk.Button(top_frame, text="返回", command=self._go_back,
            font=("Microsoft YaHei UI", 12), bg="#f8f9fa", fg="#7f8c8d", relief="flat", padx=10)
        back_btn.pack(side="left")
        settings_btn = tk.Button(top_frame, text="⚙", command=self._open_settings,
            font=("Arial", 24), bg="#f8f9fa", fg="#34495e", relief="flat", width=3, height=1)
        settings_btn.pack(side="right")
        self._pairing_btn = tk.Button(top_frame, text="📱", command=self._open_phone_pairing,
            font=("Arial", 18), bg="#f8f9fa", fg="#34495e", relief="flat", width=3, height=1)
        self._pairing_btn.pack(side="right", padx=(0, 5))
        timer_frame = tk.Frame(self, bg="#ffffff")
        timer_frame.pack(fill="both", expand=True, padx=40, pady=(5, 10))
        self.canvas = tk.Canvas(timer_frame, width=400, height=400, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(pady=(0, 10))
        self.circle_radius = 160; self.circle_center = 200; self.circle_width = 12
        self.circle_bg = "#e0e0e0"; self.circle_fg = "#3498db"
        self._draw_background_circle()
        self.update_time_label()
        self.status_label = tk.Label(timer_frame, text="准备开始",
            font=("Microsoft YaHei UI", 14), bg="#ffffff", fg="#7f8c8d")
        self.status_label.pack(pady=5)
        control_frame = tk.Frame(timer_frame, bg="#ffffff")
        control_frame.pack(pady=(10, 0), fill="x")
        self.start_btn = tk.Button(control_frame, text="开始", command=self._toggle_timer,
            font=("Microsoft YaHei UI", 18, "bold"), bg="#ffffff", fg="#3498db",
            relief="flat", padx=80, pady=18, borderwidth=2,
            highlightbackground="#3498db", highlightcolor="#3498db")
        self.start_btn.pack(pady=(0, 10))
        self.reset_btn = tk.Button(control_frame, text="重置", command=self._reset_timer,
            font=("Microsoft YaHei UI", 14), bg="#ffffff", fg="#7f8c8d", relief="flat", padx=40, pady=12)
        self.reset_btn.pack()
        self.white_noise_btn = tk.Button(control_frame, text="🌲 播放白噪音", command=self._toggle_white_noise,
            font=("Microsoft YaHei UI", 12), bg="#27ae60", fg="white", relief="flat", padx=30, pady=10, state="disabled")
        self.white_noise_btn.pack(pady=(15, 0))
        self.update_time_label()

    def _draw_background_circle(self):
        self.canvas.create_oval(self.circle_center - self.circle_radius, self.circle_center - self.circle_radius,
            self.circle_center + self.circle_radius, self.circle_center + self.circle_radius,
            outline=self.circle_bg, width=self.circle_width)

    def _draw_progress_circle(self, progress):
        self.canvas.delete("progress")
        start_angle = -90
        end_angle = start_angle + (360 * progress)
        self.canvas.create_arc(self.circle_center - self.circle_radius, self.circle_center - self.circle_radius,
            self.circle_center + self.circle_radius, self.circle_center + self.circle_radius,
            start=start_angle, extent=end_angle - start_angle,
            outline=self.circle_fg, width=self.circle_width, tags="progress", style="arc")

    def update_time_label(self):
        time_text = self.timer.get_remaining_text()
        self.canvas.delete("time_text")
        self.canvas.create_text(self.circle_center, self.circle_center, text=time_text,
            font=("Microsoft YaHei UI", 56, "bold"), fill="#2c3e50", tags="time_text")
        self._draw_progress_circle(self.timer.get_progress())

    def _toggle_timer(self):
        if self.timer.state == TimerState.IDLE:
            self.timer.start(); self.start_btn.config(text="暂停", fg="#e74c3c", highlightbackground="#e74c3c")
            self.status_label.config(text="专注进行中"); self.white_noise_btn.config(state="normal")
            self.window_monitor._distraction_cooldown.clear(); self.window_monitor.start()
            self._session_start_network()
        elif self.timer.state == TimerState.RUNNING:
            self.timer.pause(); self.start_btn.config(text="继续", fg="#27ae60", highlightbackground="#27ae60")
            self.status_label.config(text="已暂停"); self.window_monitor.pause()
        elif self.timer.state == TimerState.PAUSED:
            self.timer.start(); self.start_btn.config(text="暂停", fg="#e74c3c", highlightbackground="#e74c3c")
            self.status_label.config(text="专注进行中"); self.window_monitor.resume()

    def _toggle_white_noise(self):
        config = self.config_manager.get_all()
        volume = config.get("white_noise_volume", 0.5)
        noise_type = config.get("white_noise_type", "forest")
        if not self.white_noise_playing:
            if self.audio_player.play_white_noise(volume=volume, noise_type=noise_type):
                self.white_noise_playing = True; self.white_noise_paused = False
                self.white_noise_btn.config(text="🌲 暂停白噪音")
        elif self.white_noise_paused:
            self.audio_player.unpause_white_noise(); self.white_noise_paused = False
            self.white_noise_btn.config(text="🌲 暂停白噪音")
        else:
            self.audio_player.pause_white_noise(); self.white_noise_paused = True
            self.white_noise_btn.config(text="🌲 继续白噪音")

    def _reset_timer(self):
        if self.window_monitor.is_running(): self.window_monitor.stop()
        self.timer.reset(); self.start_btn.config(text="开始", fg="#3498db", highlightbackground="#3498db")
        self.status_label.config(text="准备开始"); self.is_micro_break = False
        self._stop_white_noise(); self.white_noise_btn.config(state="disabled"); self.update_time_label()

    def _stop_white_noise(self):
        if self.white_noise_playing:
            self.audio_player.stop_white_noise()
            self.white_noise_playing = False; self.white_noise_paused = False
            self.white_noise_btn.config(text="🌲 播放白噪音")

    def _go_back(self):
        if self.window_monitor.is_running(): self.window_monitor.stop()
        self.timer.reset(); self._stop_white_noise()
        self.http_receiver.stop(); self.udp_broadcaster.close(); self._cleanup()
        if hasattr(self, 'parent'): self.parent.deiconify()
        self.destroy()

    def _open_settings(self):
        settings_window = SettingsWindow(self, self.config_manager.get_all())
        settings_window.on_save = self._on_settings_save
        settings_window.mainloop()

    def _on_settings_save(self, config):
        for key, value in config.items(): self.config_manager.set(key, value)
        self.config_manager.save_config()
        self.timer.set_times(focus_time=config["focus_time"], break_time=config["break_time"],
            min_interval=config["min_interval"], max_interval=config["max_interval"],
            micro_break=config["micro_break"], alert_count=config.get("alert_count", 1))
        self.update_time_label(); self._reset_timer()

    def _on_timer_tick(self, remaining, total, is_micro_break=False):
        if is_micro_break:
            time_text = f"{int(remaining)}秒"; self.canvas.delete("time_text")
            self.canvas.create_text(self.circle_center, self.circle_center, text=time_text,
                font=("Microsoft YaHei UI", 40, "bold"), fill="#2c3e50", tags="time_text")
            self._draw_progress_circle((total - remaining) / total)
        else:
            self.update_time_label()

    def _on_timer_complete(self):
        config = self.config_manager.get_all()
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=config.get("volume", 0.5))
        messagebox.showinfo("完成", "专注时间结束！")
        stats_manager = StatsManager()
        stats_manager.add_focus_time(stats_manager.get_today_str(), config["focus_time"])
        self.http_receiver.set_session_stopped()
        if self.pairing_manager.is_paired() and self._session_id:
            self.udp_broadcaster.notify_session_stop(self._session_id, self.pairing_manager.get_token())
        activities = self.window_monitor.stop() if self.window_monitor.is_running() else []
        self._phone_reports = self.http_receiver.get_pending_reports()
        self._reset_timer()
        self.after(4000, lambda: self._show_assessment(activities, config["focus_time"]))

    def _show_assessment(self, activities, focus_time):
        if self.timer.state != TimerState.IDLE: return
        self._phone_reports.extend(self.http_receiver.get_pending_reports())
        self._merge_phone_activities(activities)
        if activities:
            try:
                from gui.self_assessment_window import SelfAssessmentWindow
                assessment_window = SelfAssessmentWindow(self, activities, focus_time)
                assessment_window.on_save = self._on_assessment_save
                assessment_window.mainloop()
            except Exception as e:
                print(f"打开评估窗口失败: {e}")

    def _on_assessment_save(self, activities):
        try:
            config = self.config_manager.get_all()
            self._phone_reports.extend(self.http_receiver.get_pending_reports())
            self._merge_phone_activities(activities)
            self.activity_storage.add_session_record(activities, config["focus_time"])
            self.distraction_blacklist.reload()
        except Exception as e:
            print(f"保存活动记录失败: {e}")

    def _merge_phone_activities(self, activities):
        merged_count = 0
        for report in self._phone_reports:
            for act in report.get("activities", []):
                activities.append({
                    "app_name": act.get("package_name", "unknown"),
                    "window_title": act.get("app_name", "手机App"),
                    "window_hash": f"phone_{act.get('package_name', '')}",
                    "domain": "",
                    "duration": round(act.get("duration", 0), 1),
                    "first_seen": "", "last_seen": "",
                    "switch_count": act.get("switch_count", 0),
                    "window_category": "", "user_custom_category": "",
                    "is_distracting": None, "user_notes": "",
                    "_source": "phone",
                })
                merged_count += 1
        self._phone_reports.clear()
        if merged_count: print(f"已合并 {merged_count} 条手机活动记录")

    def _session_start_network(self):
        self._session_id = uuid.uuid4().hex; self._phone_reports = []
        self.http_receiver.set_session_active(self._session_id)
        if not self.http_receiver.is_running(): self.http_receiver.start()
        if self.pairing_manager.is_paired():
            self.udp_broadcaster.notify_session_start(self._session_id, self.pairing_manager.get_token())

    def _on_phone_report(self, data: dict) -> bool:
        token = data.get("token", "")
        if self.pairing_manager.is_paired(): return self.pairing_manager.verify_token(token)
        return False

    def _on_pair_confirm(self, token: str, device_name: str) -> bool:
        if token == self.pairing_manager.get_token():
            self.pairing_manager.confirm_pairing(device_name)
            return True
        return False

    def _open_phone_pairing(self):
        if not self.http_receiver.is_running(): self.http_receiver.start()
        PhonePairingWindow(self, self.pairing_manager)

    def _on_distraction_detected(self, app_name: str, domain: str, window_title: str):
        msg = f"⚠ 你曾标记过 '{domain}' 是分心来源\n注意收回你的注意力哦 ~" if domain else f"⚠ 你曾标记过 '{app_name}' 是分心来源\n注意收回你的注意力哦 ~"
        try: self.after(0, lambda: Toast.show(self, msg, is_warning=True))
        except tk.TclError: pass

    def _on_random_alert(self):
        config = self.config_manager.get_all()
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=config.get("volume", 0.5))

    def _on_micro_break_start(self):
        self.is_micro_break = True; self.configure(bg="#e8f5e9"); self._update_all_widgets_bg("#e8f5e9")
        self.window_monitor.pause()
        self.canvas.delete("time_text")
        self.canvas.create_text(self.circle_center, self.circle_center,
            text=f"{self.timer.micro_break}秒", font=("Microsoft YaHei UI", 40, "bold"),
            fill="#2c3e50", tags="time_text")
        self.status_label.config(text="现在，收回你的注意力，闭上眼睛去感知它")

    def _on_micro_break_end(self):
        self.is_micro_break = False; self.configure(bg="#ffffff"); self._update_all_widgets_bg("#ffffff")
        self.window_monitor.resume()
        config = self.config_manager.get_all()
        self.audio_player.play_notification(count=config.get("alert_count", 1), volume=config.get("volume", 0.5))
        self.update_time_label(); self.status_label.config(text="专注进行中")

    def _update_all_widgets_bg(self, color):
        for widget in self.winfo_children(): self._update_widget_bg(widget, color)

    def _update_widget_bg(self, widget, color):
        if hasattr(widget, "configure") and widget != self.canvas:
            try: widget.configure(bg=color)
            except: pass
        for child in widget.winfo_children(): self._update_widget_bg(child, color)

    def _cleanup(self):
        self.timer.reset(); self.audio_player.cleanup()
        self.http_receiver.stop(); self.udp_broadcaster.close()

    def destroy(self):
        self._cleanup(); super().destroy()
