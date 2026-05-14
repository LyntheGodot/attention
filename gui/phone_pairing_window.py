#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 手机配对弹窗
显示 QR 码供手机扫码配对，管理 PC-手机配对流程
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import io
from utils.network_pairing import PairingManager


class PhonePairingWindow(tk.Toplevel):
    """手机配对弹窗"""

    QR_SIZE = 260
    _bg = "#ffffff"

    def __init__(self, parent, pairing_manager: PairingManager = None):
        super().__init__(parent)
        self.parent = parent
        self.title("配对手机端")
        self.geometry("480x700")
        self.configure(bg=self._bg)
        self.resizable(False, False)

        self.pairing_manager = pairing_manager or PairingManager()
        self._qr_image_tk = None
        self._poll_id: str | None = None

        self._create_widgets()
        self._generate_and_show_qr()
        self._poll_pairing_status()

    def _create_widgets(self):
        title_frame = tk.Frame(self, bg=self._bg)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            title_frame,
            text="📱 配对手机端",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=self._bg,
            fg="#2c3e50"
        ).pack(side="left")

        close_btn = tk.Button(
            title_frame,
            text="✕",
            command=self.destroy,
            font=("Arial", 18),
            bg=self._bg,
            fg="#7f8c8d",
            relief="flat",
            width=2
        )
        close_btn.pack(side="right")
        close_btn.bind("<Enter>", lambda e: close_btn.configure(fg="#e74c3c"))
        close_btn.bind("<Leave>", lambda e: close_btn.configure(fg="#7f8c8d"))

        info_frame = tk.Frame(self, bg="#f8f9fa", padx=20, pady=15)
        info_frame.pack(fill="x", padx=20, pady=(0, 15))

        self._info_label = tk.Label(
            info_frame,
            text="1. 在 Android 手机上安装「注意力番茄钟」App\n"
                 "2. 打开 App 并点击「扫码配对」\n"
                 "3. 将手机摄像头对准下方二维码",
            font=("Microsoft YaHei UI", 11),
            bg="#f8f9fa",
            fg="#2c3e50",
            justify="left"
        )
        self._info_label.pack()

        qr_frame = tk.Frame(self, bg=self._bg)
        qr_frame.pack(pady=(10, 15))

        self._qr_label = tk.Label(qr_frame, bg=self._bg, text="正在生成二维码...")
        self._qr_label.pack()

        self._status_label = tk.Label(
            self,
            text="等待手机扫码...",
            font=("Microsoft YaHei UI", 13),
            bg=self._bg,
            fg="#7f8c8d"
        )
        self._status_label.pack(pady=(0, 5))

        json_frame = tk.Frame(self, bg="#f8f9fa", padx=10, pady=8)
        json_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            json_frame,
            text="模拟器/手动输入:",
            font=("Microsoft YaHei UI", 9),
            bg="#f8f9fa",
            fg="#7f8c8d"
        ).pack(anchor="w")

        self._json_text = tk.Text(
            json_frame,
            height=4,
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#2c3e50",
            relief="solid",
            borderwidth=1,
            wrap="word"
        )
        self._json_text.pack(fill="x", pady=(4, 0))
        self._json_text.insert("1.0", "等待生成...")
        self._json_text.config(state="disabled")

        copy_btn = tk.Button(
            json_frame,
            text="复制 JSON",
            command=self._copy_json,
            font=("Microsoft YaHei UI", 10),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=12,
            pady=4
        )
        copy_btn.pack(anchor="e", pady=(4, 0))
        copy_btn.bind("<Enter>", lambda e: copy_btn.configure(bg="#2980b9"))
        copy_btn.bind("<Leave>", lambda e: copy_btn.configure(bg="#3498db"))

        self._paired_info_frame = tk.Frame(self, bg=self._bg)
        self._paired_device_label = tk.Label(
            self._paired_info_frame,
            text="",
            font=("Microsoft YaHei UI", 12),
            bg=self._bg,
            fg="#27ae60"
        )
        self._paired_device_label.pack()

        btn_frame = tk.Frame(self, bg=self._bg)
        btn_frame.pack(pady=(15, 20))

        self._regenerate_btn = tk.Button(
            btn_frame,
            text="🔄 重新生成二维码",
            command=self._generate_and_show_qr,
            font=("Microsoft YaHei UI", 12),
            bg="#3498db",
            fg="white",
            relief="flat",
            padx=20,
            pady=8
        )
        self._regenerate_btn.pack(side="left", padx=(0, 10))
        self._regenerate_btn.bind("<Enter>", lambda e: self._regenerate_btn.configure(bg="#2980b9"))
        self._regenerate_btn.bind("<Leave>", lambda e: self._regenerate_btn.configure(bg="#3498db"))

        self._unpair_btn = tk.Button(
            btn_frame,
            text="取消配对",
            command=self._unpair,
            font=("Microsoft YaHei UI", 12),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=20,
            pady=8
        )
        self._unpair_btn.pack(side="left")
        self._refresh_ui()

    def _generate_and_show_qr(self):
        try:
            import qrcode
            from qrcode.image.styledpil import StyledPilImage
        except ImportError:
            self._show_qr_fallback()
            return

        self._status_label.config(text="正在生成二维码...", fg="#7f8c8d")

        def _do():
            try:
                if not self.pairing_manager.is_paired():
                    self.pairing_manager.generate_pairing()
                qr_json = self.pairing_manager.get_qr_json_string()
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=2,
                )
                qr.add_data(qr_json)
                qr.make(fit=True)
                img = qr.make_image(fill_color="#2c3e50", back_color="white")
                img = img.resize((self.QR_SIZE, self.QR_SIZE), Image.LANCZOS)
                self._qr_image_tk = ImageTk.PhotoImage(img)
                self.after(0, self._show_qr_image)
            except Exception as e:
                self.after(0, lambda: self._show_qr_fallback(str(e)))

        threading.Thread(target=_do, daemon=True).start()

    def _show_qr_image(self):
        self._qr_label.config(image=self._qr_image_tk, text="")
        ip = self.pairing_manager.get_local_ip()
        self._status_label.config(
            text=f"本机 IP: {ip}  |  等待手机扫码...",
            fg="#7f8c8d"
        )
        qr_json = self.pairing_manager.get_qr_json_string()
        self._json_text.config(state="normal")
        self._json_text.delete("1.0", "end")
        self._json_text.insert("1.0", qr_json)
        self._json_text.config(state="disabled")
        self._refresh_ui()

    def _copy_json(self):
        json_str = self._json_text.get("1.0", "end").strip()
        if json_str and json_str != "等待生成...":
            self.clipboard_clear()
            self.clipboard_append(json_str)
            self._status_label.config(text="已复制到剪贴板！", fg="#27ae60")

    def _poll_pairing_status(self):
        if self.pairing_manager.is_paired():
            self._status_label.config(
                text=f"✅ 已配对: {self.pairing_manager.get_device_name()}",
                fg="#27ae60"
            )
            self._paired_device_label.config(
                text=f"✅ 已配对: {self.pairing_manager.get_device_name()}"
            )
            self._paired_info_frame.pack(pady=(0, 5))
            self._unpair_btn.config(state="normal")
        self._poll_id = self.after(1000, self._poll_pairing_status)

    def _show_qr_fallback(self, error: str = ""):
        msg = "二维码生成失败\n请安装依赖: pip install qrcode\n\n" if error else ""
        self._status_label.config(
            text=f"{msg}请在手机端手动输入:\nIP: {self.pairing_manager.get_local_ip()}\n"
                 f"Token: {self.pairing_manager.get_token()[:16]}...",
            fg="#e74c3c"
        )

    def _unpair(self):
        if messagebox.askyesno("确认", "确定要取消当前配对吗？"):
            self.pairing_manager.unpair()
            self._refresh_ui()
            self._status_label.config(text="已取消配对", fg="#e74c3c")
            self._paired_device_label.config(text="")

    def _refresh_ui(self):
        if self.pairing_manager.is_paired():
            device = self.pairing_manager.get_device_name()
            self._paired_device_label.config(
                text=f"✅ 已配对: {device}"
            )
            self._paired_info_frame.pack(pady=(0, 5))
            self._unpair_btn.config(state="normal")
        else:
            self._paired_info_frame.pack_forget()
            self._unpair_btn.config(state="disabled")

    def destroy(self):
        if self._poll_id:
            self.after_cancel(self._poll_id)
        super().destroy()
