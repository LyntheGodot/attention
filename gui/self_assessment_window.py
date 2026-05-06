#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 自我评估弹窗界面
专注结束后弹出，让用户标注活动分类和分心行为
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Callable
from utils.category_mapper import CategoryMapper


class SelfAssessmentWindow(tk.Toplevel):
    """自我评估弹窗"""

    def __init__(self, parent, activities: List[dict], focus_duration: int):
        """
        初始化评估窗口
        :param parent: 父窗口
        :param activities: 活动记录列表（来自WindowMonitor.stop()）
        :param focus_duration: 本次专注时长（分钟）
        """
        super().__init__(parent)
        self.parent = parent
        self.activities = activities
        self.focus_duration = focus_duration
        self.on_save: Optional[Callable[[List[dict]], None]] = None

        self.title("专注评估")
        self.geometry("850x650")
        self.configure(bg="#ffffff")
        self.resizable(False, False)

        self.category_mapper = CategoryMapper()
        self.activity_widgets: List[dict] = []  # 存储每个活动的控件引用

        # 过滤短时窗口（≤0.1分钟 = 6秒视为无效数据）
        self._filter_short_activities()

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 标题栏
        title_frame = tk.Frame(self, bg="#ffffff")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            title_frame,
            text="本次专注评估",
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

        # 统计信息区域
        stats_frame = tk.Frame(self, bg="#f8f9fa", padx=20, pady=15)
        stats_frame.pack(fill="x", padx=20, pady=(0, 15))

        total_duration = sum(act["duration"] for act in self.activities)
        total_switches = sum(act["switch_count"] for act in self.activities)

        tk.Label(
            stats_frame,
            text=f"📊 总专注时长: {self.focus_duration} 分钟",
            font=("Microsoft YaHei UI", 12),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).grid(row=0, column=0, sticky="w", padx=(0, 30))

        tk.Label(
            stats_frame,
            text=f"🔄 窗口切换次数: {total_switches} 次",
            font=("Microsoft YaHei UI", 12),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).grid(row=0, column=1, sticky="w", padx=(0, 30))

        self.distraction_ratio_label = tk.Label(
            stats_frame,
            text="⚠️ 分心占比: 0%",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#e74c3c"
        )
        self.distraction_ratio_label.grid(row=0, column=2, sticky="w")

        # 活动列表区域
        list_frame = tk.Frame(self, bg="#ffffff")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # 列表标题
        header_frame = tk.Frame(list_frame, bg="#ffffff")
        header_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            header_frame,
            text="应用/页面",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            width=35,
            anchor="w"
        ).grid(row=0, column=0, padx=(0, 10))

        tk.Label(
            header_frame,
            text="时长",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            width=6,
            anchor="w"
        ).grid(row=0, column=1, padx=(0, 5))

        tk.Label(
            header_frame,
            text="分类",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            width=12,
            anchor="w"
        ).grid(row=0, column=2, padx=(0, 10))

        tk.Label(
            header_frame,
            text="分心",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            width=5,
            anchor="center"
        ).grid(row=0, column=3, padx=(0, 5))

        tk.Label(
            header_frame,
            text="备注",
            font=("Microsoft YaHei UI", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50",
            width=18,
            anchor="w"
        ).grid(row=0, column=4, sticky="w")

        # 分隔线
        ttk.Separator(list_frame, orient="horizontal").pack(fill="x", pady=(0, 10))

        # 滚动容器
        canvas = tk.Canvas(list_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 绑定鼠标滚轮滚动
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建活动条目
        self._create_activity_items()

        # 初始化自动分类映射
        self._init_auto_mapping()

        # 底部按钮区域
        button_frame = tk.Frame(self, bg="#ffffff")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = tk.Button(
            button_frame,
            text="保存",
            command=self._save_assessment,
            font=("Microsoft YaHei UI", 14, "bold"),
            bg="#27ae60",
            fg="white",
            relief="flat",
            padx=30,
            pady=10
        )
        save_btn.pack(side="right")
        save_btn.bind("<Enter>", lambda e: save_btn.configure(bg="#219a52"))
        save_btn.bind("<Leave>", lambda e: save_btn.configure(bg="#27ae60"))

        cancel_btn = tk.Button(
            button_frame,
            text="跳过",
            command=self.destroy,
            font=("Microsoft YaHei UI", 14),
            bg="#95a5a6",
            fg="white",
            relief="flat",
            padx=30,
            pady=10
        )
        cancel_btn.pack(side="right", padx=(0, 15))
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.configure(bg="#7f8c8d"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.configure(bg="#95a5a6"))

        # 初始计算分心占比
        self._update_distraction_ratio()

    def _create_activity_items(self):
        """创建每个活动的条目"""
        categories = self.category_mapper.get_all_categories()

        for i, activity in enumerate(self.activities):
            item_frame = tk.Frame(self.scrollable_frame, bg="#ffffff" if i % 2 == 0 else "#f8f9fa", padx=10, pady=8)
            item_frame.pack(fill="x", pady=(0, 5))

            # 获取活动信息
            app_name = activity["app_name"]
            window_title = activity.get("window_title", "(无标题)")
            domain = activity.get("domain", "")
            duration = activity["duration"]

            # 显示应用名称 + 窗口标题
            # 如果有域名，优先显示域名
            display_title = domain if domain else window_title
            # 截断过长的标题
            if len(display_title) > 40:
                display_title = display_title[:37] + "..."

            app_label_text = f"{app_name}: {display_title}"
            app_label = tk.Label(
                item_frame,
                text=app_label_text,
                font=("Microsoft YaHei UI", 10),
                bg=item_frame.cget("bg"),
                fg="#2c3e50",
                width=35,
                anchor="w",
                wraplength=350
            )
            app_label.grid(row=0, column=0, padx=(0, 10), sticky="w")

            # 时长标签
            duration_label = tk.Label(
                item_frame,
                text=f"{duration}分钟",
                font=("Microsoft YaHei UI", 10),
                bg=item_frame.cget("bg"),
                fg="#7f8c8d",
                width=6
            )
            duration_label.grid(row=0, column=1, padx=(0, 5), sticky="w")

            # 分类选择下拉框
            recommended_category = self.category_mapper.get_recommended_category(app_name)
            # 如果没有按应用名找到，尝试按域名找
            if not recommended_category and domain:
                recommended_category = self.category_mapper.get_recommended_category(domain)

            category_var = tk.StringVar(value=recommended_category if recommended_category else categories[0])

            category_combo = ttk.Combobox(
                item_frame,
                textvariable=category_var,
                values=categories,
                state="readonly",
                font=("Microsoft YaHei UI", 10),
                width=12
            )
            category_combo.grid(row=0, column=2, padx=(0, 10), sticky="w")

            # 分心复选框
            is_distracting_var = tk.BooleanVar(value=False)
            distract_check = tk.Checkbutton(
                item_frame,
                variable=is_distracting_var,
                bg=item_frame.cget("bg"),
                activebackground=item_frame.cget("bg"),
                command=self._update_distraction_ratio
            )
            distract_check.grid(row=0, column=3, padx=(0, 5), sticky="n")

            # 备注输入框
            notes_entry = tk.Entry(
                item_frame,
                font=("Microsoft YaHei UI", 10),
                width=18,
                fg="#7f8c8d"
            )
            notes_entry.insert(0, "可选备注")
            notes_entry.grid(row=0, column=4, sticky="w")

            # 输入框焦点事件
            def on_entry_focus_in(event, entry):
                if entry.get() == "可选备注":
                    entry.delete(0, tk.END)
                    entry.config(fg="#2c3e50")

            def on_entry_focus_out(event, entry):
                if entry.get() == "":
                    entry.insert(0, "可选备注")
                    entry.config(fg="#7f8c8d")

            notes_entry.bind("<FocusIn>", lambda e, en=notes_entry: on_entry_focus_in(e, en))
            notes_entry.bind("<FocusOut>", lambda e, en=notes_entry: on_entry_focus_out(e, en))

            # 保存控件引用
            self.activity_widgets.append({
                "app_name": app_name,
                "domain": domain,
                "category_var": category_var,
                "is_distracting_var": is_distracting_var,
                "notes_entry": notes_entry
            })

    def _init_auto_mapping(self):
        """初始化自动分类映射（基于已有标注数据）"""
        # 这个方法会在用户保存标注后被调用，用于更新映射
        pass

    def _filter_short_activities(self):
        """过滤短时窗口数据（≤0.1分钟视为无效数据，如临时弹窗、右键菜单等）"""
        threshold = 0.1  # 0.1分钟 = 6秒
        original_count = len(self.activities)

        # 过滤掉时长≤阈值的数据
        self.activities = [act for act in self.activities if act.get("duration", 0) > threshold]

        filtered_count = original_count - len(self.activities)

        if filtered_count > 0:
            print(f"已过滤 {filtered_count} 条短时窗口数据（时长≤{threshold}分钟）")

    def _update_distraction_ratio(self):
        """更新分心占比显示"""
        total_duration = sum(act["duration"] for act in self.activities)
        if total_duration == 0:
            ratio = 0
        else:
            distraction_duration = 0
            for i, widget in enumerate(self.activity_widgets):
                if widget["is_distracting_var"].get():
                    distraction_duration += self.activities[i]["duration"]
            ratio = distraction_duration / total_duration

        ratio_pct = int(ratio * 100)
        self.distraction_ratio_label.config(text=f"⚠️ 分心占比: {ratio_pct}%")

    def _save_assessment(self):
        """保存评估结果"""
        try:
            # 收集每个活动的标注
            for i, widget in enumerate(self.activity_widgets):
                activity = self.activities[i]
                category = widget["category_var"].get()
                is_distracting = widget["is_distracting_var"].get()
                notes = widget["notes_entry"].get()

                activity["window_category"] = category
                activity["is_distracting"] = is_distracting
                activity["user_notes"] = notes if notes != "可选备注" else ""

                # 更新分类映射 - 同时按应用名和域名保存
                app_name = widget["app_name"]
                domain = widget.get("domain", "")

                # 保存应用名映射
                self.category_mapper.add_mapping(app_name, category)
                # 如果有域名，也保存域名映射（这样更精准）
                if domain:
                    self.category_mapper.add_mapping(domain, category)

            if self.on_save:
                self.on_save(self.activities)

            messagebox.showinfo("成功", "评估已保存！下次相同应用/网站会自动推荐分类。")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存评估失败: {e}")
            print(f"保存评估失败: {e}")
            import traceback
            traceback.print_exc()
