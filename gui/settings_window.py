#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 设置界面
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.title("设置")
        self.geometry("500x880")
        self.configure(bg="#ffffff")
        self.resizable(False, False)
        self.config = config.copy()
        self.on_save = None
        self.current_tab = "timer"
        vcmd = (self.register(self._validate_numeric), "%P")
        self._create_widgets(vcmd)

    def _validate_numeric(self, value):
        return value == "" or value.isdigit()

    def _create_widgets(self, vcmd):
        title_frame = tk.Frame(self, bg="#ffffff")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        tk.Label(title_frame, text="设置", font=("Microsoft YaHei UI", 20, "bold"),
            bg="#ffffff", fg="#2c3e50").pack(side="left")
        close_btn = tk.Button(title_frame, text="✕", command=self.destroy,
            font=("Arial", 18), bg="#ffffff", fg="#7f8c8d", relief="flat", width=2)
        close_btn.pack(side="right")
        tab_frame = tk.Frame(self, bg="#ffffff")
        tab_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.timer_tab_btn = tk.Button(tab_frame, text="计时选项",
            font=("Microsoft YaHei UI", 12), bg="#3498db", fg="white", relief="flat",
            padx=20, pady=8, command=lambda: self._switch_tab("timer"))
        self.timer_tab_btn.pack(side="left", padx=(0, 5))
        self.sound_tab_btn = tk.Button(tab_frame, text="声音",
            font=("Microsoft YaHei UI", 12), bg="#ecf0f1", fg="#7f8c8d", relief="flat",
            padx=20, pady=8, command=lambda: self._switch_tab("sound"))
        self.sound_tab_btn.pack(side="left")
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20)
        self.content_container = tk.Frame(self, bg="#ffffff")
        self.content_container.pack(fill="both", expand=True, padx=30, pady=20)
        self._create_timer_settings(vcmd)
        self._create_sound_settings()
        self._show_timer_settings()
        self._create_button_area()

    def _create_timer_settings(self, vcmd):
        self.timer_frame = tk.Frame(self.content_container, bg="#ffffff")
        self._add_entry_row("专注时间:", "分钟", self.config["focus_time"], vcmd, "focus_entry", 0)
        self._add_entry_row("最小间隔:", "分钟", self.config["min_interval"], vcmd, "min_interval_entry", 1)
        self._add_entry_row("最大间隔:", "分钟", self.config["max_interval"], vcmd, "max_interval_entry", 2)
        self._add_entry_row("微休息时间:", "秒", self.config["micro_break"], vcmd, "micro_break_entry", 3)
        self._add_entry_row("提示音次数:", "次 (0=纯净模式)", self.config.get("alert_count", 1), vcmd, "alert_count_entry", 4)
        ttk.Separator(self.timer_frame, orient="horizontal").pack(fill="x", pady=20)
        self._add_entry_row("休息时间:", "分钟", self.config["break_time"], vcmd, "break_entry", 5)
        break_countdown_frame = tk.Frame(self.timer_frame, bg="#ffffff")
        break_countdown_frame.pack(fill="x", pady=(0, 20))
        tk.Label(break_countdown_frame, text="休息倒计时:",
            font=("Microsoft YaHei UI", 14), bg="#ffffff", fg="#34495e").pack(side="left")
        self.break_countdown_var = tk.BooleanVar(value=self.config["break_countdown"])
        tk.Checkbutton(break_countdown_frame, variable=self.break_countdown_var,
            bg="#ffffff", activebackground="#ffffff").pack(side="left", padx=(20, 0))

    def _add_entry_row(self, label, unit, default_value, vcmd, attr_name, row_idx):
        frame = tk.Frame(self.timer_frame, bg="#ffffff")
        frame.pack(fill="x", pady=(0, 15))
        tk.Label(frame, text=label, font=("Microsoft YaHei UI", 14),
            bg="#ffffff", fg="#34495e").pack(side="left")
        entry = tk.Entry(frame, font=("Microsoft YaHei UI", 14), width=10,
            justify="center", validate="key", validatecommand=vcmd)
        entry.insert(0, str(default_value))
        entry.pack(side="left", padx=(20, 5))
        setattr(self, attr_name, entry)
        tk.Label(frame, text=unit, font=("Microsoft YaHei UI", 14),
            bg="#ffffff", fg="#34495e").pack(side="left")

    def _create_sound_settings(self):
        self.sound_frame = tk.Frame(self.content_container, bg="#ffffff")
        volume_section = tk.Frame(self.sound_frame, bg="#ffffff")
        volume_section.pack(fill="x", pady=(10, 0))
        vol_title = tk.Frame(volume_section, bg="#ffffff")
        vol_title.pack(fill="x", pady=(0, 20))
        tk.Label(vol_title, text="🔊", font=("Segoe UI Emoji", 32), bg="#ffffff").pack(side="left", padx=(0, 15))
        tk.Label(vol_title, text="提示音量", font=("Microsoft YaHei UI", 18, "bold"),
            bg="#ffffff", fg="#2c3e50").pack(side="left")
        slider_frame = tk.Frame(volume_section, bg="#ffffff")
        slider_frame.pack(fill="x", pady=(10, 20))
        tk.Label(slider_frame, text="🔈", font=("Segoe UI Emoji", 16), bg="#ffffff").pack(side="left", padx=(0, 10))
        self.volume_var = tk.DoubleVar(value=self.config.get("volume", 0.5) * 100)
        style = ttk.Style()
        style.configure("Volume.Horizontal.TScale", background="#ffffff", troughcolor="#ecf0f1", sliderlength=30, sliderthickness=20)
        self.volume_scale = ttk.Scale(slider_frame, from_=0, to=100, orient="horizontal",
            variable=self.volume_var, style="Volume.Horizontal.TScale", command=self._on_volume_change)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.volume_label = tk.Label(slider_frame, text=f"{int(self.config.get('volume', 0.5) * 100)}%",
            font=("Microsoft YaHei UI", 14, "bold"), bg="#ffffff", fg="#3498db", width=5)
        self.volume_label.pack(side="left")
        test_frame = tk.Frame(self.sound_frame, bg="#ffffff")
        test_frame.pack(fill="x", pady=(30, 0))
        test_btn = tk.Button(test_frame, text="🔊 试听提示音", font=("Microsoft YaHei UI", 12),
            bg="#3498db", fg="white", relief="flat", padx=30, pady=12, command=self._test_sound)
        test_btn.pack(side="left")
        ttk.Separator(self.sound_frame, orient="horizontal").pack(fill="x", pady=40)
        wn_section = tk.Frame(self.sound_frame, bg="#ffffff")
        wn_section.pack(fill="x")
        wn_title = tk.Frame(wn_section, bg="#ffffff")
        wn_title.pack(fill="x", pady=(0, 20))
        tk.Label(wn_title, text="🌲", font=("Segoe UI Emoji", 32), bg="#ffffff").pack(side="left", padx=(0, 15))
        tk.Label(wn_title, text="白噪音音量", font=("Microsoft YaHei UI", 18, "bold"),
            bg="#ffffff", fg="#2c3e50").pack(side="left")
        type_frame = tk.Frame(wn_section, bg="#ffffff")
        type_frame.pack(fill="x", pady=(0, 20))
        tk.Label(type_frame, text="白噪音类型:", font=("Microsoft YaHei UI", 14),
            bg="#ffffff", fg="#34495e").pack(side="left")
        self.white_noise_type_var = tk.StringVar(
            value="🌲 森林" if self.config.get("white_noise_type", "forest") == "forest" else "⛈️ 雷雨")
        ttk.Combobox(type_frame, textvariable=self.white_noise_type_var,
            values=["🌲 森林", "⛈️ 雷雨"], state="readonly",
            font=("Microsoft YaHei UI", 12), width=15).pack(side="left", padx=(20, 0))
        wn_slider = tk.Frame(wn_section, bg="#ffffff")
        wn_slider.pack(fill="x", pady=(10, 20))
        tk.Label(wn_slider, text="🔈", font=("Segoe UI Emoji", 16), bg="#ffffff").pack(side="left", padx=(0, 10))
        self.white_noise_volume_var = tk.DoubleVar(value=self.config.get("white_noise_volume", 0.5) * 100)
        self.white_noise_volume_scale = ttk.Scale(wn_slider, from_=0, to=100, orient="horizontal",
            variable=self.white_noise_volume_var, style="Volume.Horizontal.TScale", command=self._on_white_noise_volume_change)
        self.white_noise_volume_scale.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.white_noise_volume_label = tk.Label(wn_slider, text=f"{int(self.config.get('white_noise_volume', 0.5) * 100)}%",
            font=("Microsoft YaHei UI", 14, "bold"), bg="#ffffff", fg="#27ae60", width=5)
        self.white_noise_volume_label.pack(side="left")

    def _create_button_area(self):
        button_frame = tk.Frame(self, bg="#ffffff")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        save_btn = tk.Button(button_frame, text="保存", command=self._save_settings,
            font=("Microsoft YaHei UI", 14, "bold"), bg="#3498db", fg="white", relief="flat", padx=30, pady=10)
        save_btn.pack(side="right")
        reset_btn = tk.Button(button_frame, text="重置", command=self._reset_settings,
            font=("Microsoft YaHei UI", 14), bg="#95a5a6", fg="white", relief="flat", padx=30, pady=10)
        reset_btn.pack(side="left")

    def _switch_tab(self, tab_name):
        self.current_tab = tab_name
        if tab_name == "timer":
            self.timer_tab_btn.configure(bg="#3498db", fg="white")
            self.sound_tab_btn.configure(bg="#ecf0f1", fg="#7f8c8d")
            self._show_timer_settings()
        else:
            self.sound_tab_btn.configure(bg="#3498db", fg="white")
            self.timer_tab_btn.configure(bg="#ecf0f1", fg="#7f8c8d")
            self._show_sound_settings()

    def _show_timer_settings(self):
        for widget in self.content_container.winfo_children(): widget.pack_forget()
        self.timer_frame.pack(fill="both", expand=True)

    def _show_sound_settings(self):
        for widget in self.content_container.winfo_children(): widget.pack_forget()
        self.sound_frame.pack(fill="both", expand=True)

    def _on_volume_change(self, value):
        self.volume_label.configure(text=f"{int(float(value))}%")

    def _on_white_noise_volume_change(self, value):
        self.white_noise_volume_label.configure(text=f"{int(float(value))}%")

    def _test_sound(self):
        volume = self.volume_var.get() / 100.0
        try:
            if hasattr(self.parent, 'audio_player'):
                config = self.parent.config_manager.get_all() if hasattr(self.parent, 'config_manager') else {}
                self.parent.audio_player.play_notification(count=config.get("alert_count", 1), volume=volume)
            else:
                from utils.audio import AudioPlayer
                AudioPlayer().play_notification(count=1, volume=volume)
        except Exception as e:
            print(f"播放测试音失败: {e}")

    def _save_settings(self):
        try:
            self.config["volume"] = self.volume_var.get() / 100.0
            self.config["white_noise_volume"] = self.white_noise_volume_var.get() / 100.0
            type_text = self.white_noise_type_var.get()
            self.config["white_noise_type"] = "forest" if "森林" in type_text else "thunderstorm"
            if self.current_tab == "timer":
                focus_time = int(self.focus_entry.get() or "0")
                break_time = int(self.break_entry.get() or "0")
                min_interval = int(self.min_interval_entry.get() or "0")
                max_interval = int(self.max_interval_entry.get() or "0")
                micro_break = int(self.micro_break_entry.get() or "0")
                break_countdown = self.break_countdown_var.get()
                alert_count = int(self.alert_count_entry.get() or "1")
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
                if alert_count < 0 or alert_count > 5:
                    raise ValueError("提示音次数必须在0-5次之间")
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
        if messagebox.askyesno("确认", "确定要重置为默认设置吗？"):
            self.volume_var.set(50); self.volume_label.configure(text="50%")
            self.white_noise_volume_var.set(50); self.white_noise_volume_label.configure(text="50%")
            self.white_noise_type_var.set("🌲 森林")
            if hasattr(self, 'focus_entry'):
                self.focus_entry.delete(0, tk.END); self.focus_entry.insert(0, "40")
            if hasattr(self, 'break_entry'):
                self.break_entry.delete(0, tk.END); self.break_entry.insert(0, "5")
            if hasattr(self, 'min_interval_entry'):
                self.min_interval_entry.delete(0, tk.END); self.min_interval_entry.insert(0, "5")
            if hasattr(self, 'max_interval_entry'):
                self.max_interval_entry.delete(0, tk.END); self.max_interval_entry.insert(0, "40")
            if hasattr(self, 'micro_break_entry'):
                self.micro_break_entry.delete(0, tk.END); self.micro_break_entry.insert(0, "60")
            if hasattr(self, 'break_countdown_var'):
                self.break_countdown_var.set(True)
            if hasattr(self, 'alert_count_entry'):
                self.alert_count_entry.delete(0, tk.END); self.alert_count_entry.insert(0, "1")
