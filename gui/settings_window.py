#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 设置界面
用于配置各种时间参数
"""

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsWindow(tk.Toplevel):
    """设置窗口"""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.parent = parent
        self.title("计时选项")
        self.geometry("500x650")
        self.configure(bg="#ffffff")
        self.resizable(False, False)

        self.config = config.copy()
        self.on_save = None

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
            text="计时选项",
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

        # 设置内容区域
        content_frame = tk.Frame(self, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # 专注时间
        focus_frame = tk.Frame(content_frame, bg="#ffffff")
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
        min_interval_frame = tk.Frame(content_frame, bg="#ffffff")
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
        max_interval_frame = tk.Frame(content_frame, bg="#ffffff")
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
        micro_break_frame = tk.Frame(content_frame, bg="#ffffff")
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
        alert_count_frame = tk.Frame(content_frame, bg="#ffffff")
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
        ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=20)

        # 休息时间
        break_frame = tk.Frame(content_frame, bg="#ffffff")
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
        break_countdown_frame = tk.Frame(content_frame, bg="#ffffff")
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

        # 按钮区域
        button_frame = tk.Frame(content_frame, bg="#ffffff")
        button_frame.pack(fill="x", pady=20)

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

    def _save_settings(self):
        """保存设置"""
        try:
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
            self.focus_entry.delete(0, tk.END)
            self.focus_entry.insert(0, "40")
            self.break_entry.delete(0, tk.END)
            self.break_entry.insert(0, "5")
            self.min_interval_entry.delete(0, tk.END)
            self.min_interval_entry.insert(0, "5")
            self.max_interval_entry.delete(0, tk.END)
            self.max_interval_entry.insert(0, "40")
            self.micro_break_entry.delete(0, tk.END)
            self.micro_break_entry.insert(0, "60")
            self.break_countdown_var.set(True)
            self.alert_count_entry.delete(0, tk.END)
            self.alert_count_entry.insert(0, "1")
