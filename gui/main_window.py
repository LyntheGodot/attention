#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 主界面
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.pomodoro_window import PomodoroWindow
from gui.stats_window import StatsWindow


class MainWindow(tk.Tk):
    """主界面窗口"""

    def __init__(self):
        super().__init__()
        self.title("Attention is all you need!")
        self.geometry("600x500")
        self.configure(bg="#f8f9fa")
        self.resizable(False, False)
        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(
            self,
            text="Attention is all you need!",
            font=("Microsoft YaHei UI", 24, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(pady=(60, 40))

        # 按钮容器
        button_frame = tk.Frame(self, bg="#f8f9fa")
        button_frame.pack(pady=20, fill="both", expand=True)

        # 随机番茄钟按钮
        pomodoro_btn = tk.Button(
            button_frame,
            text="随机番茄钟",
            command=self._start_pomodoro,
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=40,
            pady=25,
            width=20
        )
        pomodoro_btn.pack(pady=(0, 20))
        pomodoro_btn.bind("<Enter>", lambda e: pomodoro_btn.configure(bg="#2980b9"))
        pomodoro_btn.bind("<Leave>", lambda e: pomodoro_btn.configure(bg="#3498db"))

        # 统计按钮
        stats_btn = tk.Button(
            button_frame,
            text="统计",
            command=self._show_stats,
            font=("Microsoft YaHei UI", 16),
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=40,
            pady=20,
            width=20
        )
        stats_btn.pack(pady=(0, 20))
        stats_btn.bind("<Enter>", lambda e: stats_btn.configure(bg="#219a52"))
        stats_btn.bind("<Leave>", lambda e: stats_btn.configure(bg="#27ae60"))

        # 说明按钮
        info_btn = tk.Button(
            button_frame,
            text="说明",
            command=self._show_info,
            font=("Microsoft YaHei UI", 16),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            padx=40,
            pady=20,
            width=20
        )
        info_btn.pack(pady=(0, 20))
        info_btn.bind("<Enter>", lambda e: info_btn.configure(bg="#7f8c8d"))
        info_btn.bind("<Leave>", lambda e: info_btn.configure(bg="#95a5a6"))

        # 底部信息
        footer_label = tk.Label(
            self,
            text="专注当下 · 感知自我",
            font=("Microsoft YaHei UI", 12),
            bg="#f8f9fa",
            fg="#7f8c8d"
        )
        footer_label.pack(side="bottom", pady=20)

    def _start_pomodoro(self):
        """启动番茄钟"""
        self.withdraw()
        try:
            pomodoro_window = PomodoroWindow(self)
            pomodoro_window.protocol("WM_DELETE_WINDOW", lambda: self._on_pomodoro_close(pomodoro_window))
            pomodoro_window.mainloop()
        except Exception as e:
            messagebox.showerror("错误", f"启动番茄钟失败: {e}")
            self.deiconify()

    def _on_pomodoro_close(self, window):
        """番茄钟窗口关闭事件"""
        window.destroy()
        self.deiconify()

    def _show_stats(self):
        """显示统计页面"""
        self.withdraw()
        try:
            stats_window = StatsWindow(self)
            stats_window.protocol("WM_DELETE_WINDOW", lambda: self._on_stats_close(stats_window))
            stats_window.mainloop()
        except Exception as e:
            messagebox.showerror("错误", f"打开统计页面失败: {e}")
            self.deiconify()

    def _on_stats_close(self, window):
        """统计页面关闭事件"""
        window.destroy()
        self.deiconify()

    def _show_info(self):
        """显示说明信息"""
        info_text = """
        这是一个帮助您培养专注力的番茄钟应用。

        **功能特点：**
        - 可视化进度圆环，直观显示专注进度
        - 随机注意力提示：在专注过程中随机提醒您"收回注意力"
        - 微休息界面：提示时会显示浅绿色界面，帮助您放松
        - 灵活的设置：可调整专注时间、休息时间和提示间隔

        **使用方法：**
        1. 点击"随机番茄钟"开始
        2. 在番茄钟界面右上角点击设置图标调整参数
        3. 专注过程中会随机播放提示音
        4. 听到提示音后，请按照提示进行短暂休息

        **提示说明：**
        - 最小间隔和最大间隔决定了提示音出现的时间范围
        - 微休息时间建议设置为30秒到2分钟
        - 最大间隔不能超过专注时间

        祝您专注愉快！
        """
        messagebox.showinfo("应用说明", info_text)

    def run(self):
        """运行主循环"""
        self.mainloop()
