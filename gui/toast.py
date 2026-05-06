#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - Toast 提醒浮层
半透明、不抢焦点的短暂提醒，用于分心行为预警
"""

import tkinter as tk


class Toast:
    """半透明 Toast 提醒，3 秒后自动消失，不抢占焦点"""

    BG_COLOR = "#2c3e50"
    TEXT_COLOR = "#ffffff"
    WARN_BG = "#c0392b"
    FONT = ("Microsoft YaHei UI", 13)
    WIDTH = 420
    HEIGHT = 60
    MARGIN_RIGHT = 30
    MARGIN_BOTTOM = 80
    DURATION_MS = 3500
    FADE_STEPS = 6
    FADE_INTERVAL_MS = 50

    def __init__(self, parent: tk.Tk | tk.Toplevel, message: str, is_warning: bool = True):
        self.parent = parent
        self._popup: tk.Toplevel | None = None
        self._fade_job: str | None = None
        self._dismiss_job: str | None = None
        self._show(message, is_warning)

    def _show(self, message: str, is_warning: bool):
        bg = self.WARN_BG if is_warning else self.BG_COLOR

        self._popup = tk.Toplevel(self.parent)
        self._popup.overrideredirect(True)
        self._popup.attributes("-topmost", True)
        self._popup.attributes("-alpha", 0.92)

        # 不要让浮层抢走键盘焦点（Windows 特定）
        try:
            self._popup.wm_attributes("-disabled", True)
            self._popup.after(100, lambda: self._popup.wm_attributes("-disabled", False))
        except tk.TclError:
            pass

        frame = tk.Frame(self._popup, bg=bg, padx=2, pady=2)
        frame.pack(fill="both", expand=True)

        inner = tk.Frame(frame, bg=bg, highlightbackground="#bdc3c7", highlightthickness=1)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(
            inner,
            text=message,
            font=self.FONT,
            bg=bg,
            fg=self.TEXT_COLOR,
            padx=24,
            pady=14,
            wraplength=self.WIDTH - 60,
            justify="center"
        ).pack()

        # 定位到屏幕中央
        self._popup.update_idletasks()
        screen_w = self.parent.winfo_screenwidth()
        screen_h = self.parent.winfo_screenheight()
        x = (screen_w - self.WIDTH) // 2
        y = (screen_h - self.HEIGHT) // 2
        self._popup.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        self._dismiss_job = self._popup.after(self.DURATION_MS, self._start_fade)

    def _start_fade(self):
        if not self._popup:
            return
        self._fade_step(1.0)

    def _fade_step(self, alpha: float):
        if not self._popup or alpha <= 0:
            self.destroy()
            return
        try:
            self._popup.attributes("-alpha", alpha)
        except tk.TclError:
            return
        next_alpha = alpha - (1.0 / self.FADE_STEPS)
        self._fade_job = self._popup.after(
            self.FADE_INTERVAL_MS, lambda: self._fade_step(next_alpha)
        )

    def destroy(self):
        if self._fade_job:
            try:
                self._popup.after_cancel(self._fade_job)
            except (tk.TclError, AttributeError):
                pass
        if self._dismiss_job:
            try:
                self._popup.after_cancel(self._dismiss_job)
            except (tk.TclError, AttributeError):
                pass
        if self._popup:
            try:
                self._popup.destroy()
            except tk.TclError:
                pass
            self._popup = None

    @staticmethod
    def show(parent: tk.Tk | tk.Toplevel, message: str, is_warning: bool = True):
        """快捷方法"""
        return Toast(parent, message, is_warning)
