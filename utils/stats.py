#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 统计数据管理模块
用于记录和查询每日专注时间统计
"""

import json
import os
import sys
from datetime import datetime, timedelta


STATS_FILE = "stats.json"


def _get_user_data_path():
    """获取用户数据路径（配置和统计文件保存位置）"""
    # 如果是打包的 exe，保存在 exe 同级目录下
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        exe_path = os.path.dirname(sys.executable)
        return exe_path
    # 开发环境：项目根目录
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(utils_dir)


def _get_stats_path():
    """获取统计文件路径"""
    base_path = _get_user_data_path()
    return os.path.join(base_path, STATS_FILE)


class StatsManager:
    """统计数据管理类"""

    def __init__(self):
        self.stats = self.load_stats()

    def load_stats(self):
        """加载统计数据"""
        stats_path = _get_stats_path()
        try:
            if os.path.exists(stats_path):
                with open(stats_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"加载统计数据失败: {e}")
            return {}

    def save_stats(self):
        """保存统计数据到文件"""
        stats_path = _get_stats_path()
        try:
            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存统计数据失败: {e}")
            return False

    def add_focus_time(self, date_str, minutes):
        """
        添加专注时间

        Args:
            date_str (str): 日期字符串，格式如 "2026-03-11"
            minutes (int): 专注时长（分钟）
        """
        if date_str not in self.stats:
            self.stats[date_str] = 0
        self.stats[date_str] += minutes
        self.save_stats()

    def get_stats(self, days=14):
        """
        获取最近 N 天的统计数据

        Args:
            days (int): 获取天数，默认 14 天

        Returns:
            list: 包含日期和对应专注时间的字典列表
        """
        stats_list = []
        today = datetime.now().date()

        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            minutes = self.stats.get(date_str, 0)
            stats_list.append({"date": date_str, "minutes": minutes})

        return stats_list

    def get_total_focus_time(self):
        """
        获取总专注时间

        Returns:
            int: 总专注时间（分钟）
        """
        return sum(self.stats.values())

    def get_date_str(self, date_obj):
        """
        将日期对象转换为字符串格式

        Args:
            date_obj (datetime.date): 日期对象

        Returns:
            str: 格式化后的日期字符串（YYYY-MM-DD）
        """
        return date_obj.strftime("%Y-%m-%d")

    def get_today_str(self):
        """
        获取今天的日期字符串

        Returns:
            str: 今天的日期字符串（YYYY-MM-DD）
        """
        return self.get_date_str(datetime.now().date())
