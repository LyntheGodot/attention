#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 统计界面
包含每日专注时间可视化柱状图
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.stats import StatsManager


class StatsWindow(tk.Toplevel):
    """统计界面窗口"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("专注统计")
        self.geometry("800x600")
        self.configure(bg="#f8f9fa")
        self.resizable(False, False)

        self.stats_manager = StatsManager()

        # 创建界面
        self._create_widgets()
        # 加载统计数据并绘制图表
        self._load_and_draw_stats()

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部栏
        top_frame = tk.Frame(self, bg="#f8f9fa", height=60)
        top_frame.pack(fill="x", padx=20, pady=(10, 5))
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

        # 标题
        title_label = tk.Label(
            top_frame,
            text="专注统计",
            font=("Microsoft YaHei UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=20)

        # 统计信息面板
        info_frame = tk.Frame(self, bg="#ffffff", relief="flat", bd=2)
        info_frame.pack(fill="x", padx=40, pady=(20, 10))

        # 总专注时间
        total_time = self.stats_manager.get_total_focus_time()
        hours = total_time // 60
        mins = total_time % 60
        total_text = f"总专注时间: {hours} 小时 {mins} 分钟"

        self.total_label = tk.Label(
            info_frame,
            text=total_text,
            font=("Microsoft YaHei UI", 14),
            bg="#ffffff",
            fg="#34495e"
        )
        self.total_label.pack(pady=10)

        # 图表区域
        chart_frame = tk.Frame(self, bg="#ffffff", relief="flat", bd=2)
        chart_frame.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        # 画布用于绘制柱状图
        self.canvas = tk.Canvas(
            chart_frame,
            width=700,
            height=380,
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)

    def _load_and_draw_stats(self):
        """加载并绘制统计图表"""
        # 获取最近14天的数据
        stats = self.stats_manager.get_stats(days=14)

        # 计算最大值，用于归一化
        max_minutes = max(stat["minutes"] for stat in stats) if stats else 0
        max_value = max(10, max_minutes)  # 确保至少有10的高度

        # 绘制图表
        self._draw_chart(stats, max_value)

    def _draw_chart(self, stats, max_value):
        """绘制柱状图"""
        # 清空画布
        self.canvas.delete("all")

        # 图表尺寸参数
        chart_width = 650
        chart_height = 300
        start_x = 40
        start_y = 320
        bar_width = 35
        bar_gap = 10
        max_bar_height = 280

        # 绘制坐标轴
        self.canvas.create_line(start_x, start_y, start_x + chart_width, start_y,
                               width=2, fill="#34495e")
        self.canvas.create_line(start_x, start_y - max_bar_height, start_x, start_y,
                               width=2, fill="#34495e")

        # 绘制柱状图
        for i, stat in enumerate(stats):
            # 计算柱子位置
            x = start_x + i * (bar_width + bar_gap) + bar_gap
            y = start_y
            height = (stat["minutes"] / max_value) * max_bar_height
            height = max(2, height)  # 最小高度2像素

            # 绘制柱子背景
            self.canvas.create_rectangle(x, y - max_bar_height, x + bar_width, y,
                                       fill="#f0f0f0", outline="")

            # 绘制柱子（动画效果）
            self._draw_bar_with_animation(x, y, height, bar_width, i)

            # 绘制日期标签
            date_str = self._format_date_label(stat["date"])
            self.canvas.create_text(x + bar_width / 2, y + 20,
                                   text=date_str, font=("Microsoft YaHei UI", 10),
                                   fill="#7f8c8d")

            # 绘制数值标签
            if stat["minutes"] > 0:
                value_label = f"{stat['minutes']}m"
                self.canvas.create_text(x + bar_width / 2, y - height - 15,
                                       text=value_label, font=("Microsoft YaHei UI", 10),
                                       fill="#2c3e50")

    def _format_date_label(self, date_str):
        """格式化日期标签"""
        # 将 "2026-03-11" 格式化为 "3/11"
        parts = date_str.split("-")
        return f"{int(parts[1])}/{int(parts[2])}"

    def _draw_bar_with_animation(self, x, y, target_height, bar_width, delay):
        """绘制带动画效果的柱子"""
        # 延迟绘制，形成依次升起的效果
        self.after(delay * 50, lambda: self._animate_bar(x, y, target_height, bar_width))

    def _animate_bar(self, x, y, target_height, bar_width, current_height=0, step=2):
        """柱子动画"""
        if current_height < target_height:
            current_height = min(current_height + step, target_height)
            # 清除当前柱子
            tag = f"bar_{x}_{y}"
            self.canvas.delete(tag)
            # 绘制柱子
            self.canvas.create_rectangle(x, y - current_height, x + bar_width, y,
                                       fill="#3498db", outline="#2980b9", width=1,
                                       tags=tag)
            # 继续动画
            self.after(10, lambda: self._animate_bar(x, y, target_height, bar_width,
                                                    current_height, step))
        else:
            # 动画结束，绘制完整柱子
            tag = f"bar_{x}_{y}"
            self.canvas.delete(tag)
            self.canvas.create_rectangle(x, y - target_height, x + bar_width, y,
                                       fill="#3498db", outline="#2980b9", width=1,
                                       tags=tag)

    def _go_back(self):
        """返回主菜单"""
        if hasattr(self, 'parent'):
            self.parent.deiconify()
        self.destroy()

    def destroy(self):
        """销毁窗口时清理资源"""
        super().destroy()
