#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 窗口活动监测模块
用于监测前台窗口活动，统计应用使用情况
"""

import threading
import time
import hashlib
import os
import re
from typing import Dict, List, Optional, Callable

try:
    import win32gui
    import win32process
    import psutil
    WINDOWS_SUPPORT = True
except ImportError:
    WINDOWS_SUPPORT = False


def _extract_domain_from_title(window_title: str) -> str:
    """从窗口标题中提取域名（如果有）"""
    if not window_title:
        return ""

    patterns = [
        r'[-–—]\s*(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/\S*)?',
        r'[-–—]\s*([a-zA-Z0-9-]+\.)+(com|cn|org|net|io|co|me|cc|tv|xyz|info|biz)',
        r'[-–—]\s*([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}',
        r'\|.*?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}',
    ]

    for pattern in patterns:
        match = re.search(pattern, window_title)
        if match:
            domain_part = match.group(1) if match.lastindex and match.group(match.lastindex) else match.group(0)
            domain = domain_part.strip('-|—– ')
            if domain.startswith('http'):
                url_match = re.search(r'https?://([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}', domain)
                if url_match:
                    domain = url_match.group(0).replace('http://', '').replace('https://', '')
            return domain.lower()

    return ""


class WindowActivity:
    """窗口活动记录"""
    def __init__(self, app_name: str, window_title: str, window_hash: str, first_seen: float):
        self.app_name = app_name
        self.window_title = window_title  # 原始窗口标题
        self.window_hash = window_hash
        self.first_seen = first_seen
        self.last_seen = first_seen
        self.duration = 0
        self.switch_count = 1  # 首次出现计数1次
        self.domain = self._extract_domain()  # 从标题中提取域名

    def _extract_domain(self) -> str:
        """从窗口标题中提取域名（如果有）"""
        return _extract_domain_from_title(self.window_title)

    def update(self, timestamp: float, window_title: str = None):
        """更新活动时间"""
        self.duration += timestamp - self.last_seen
        self.last_seen = timestamp
        if window_title and window_title != self.window_title:
            # 窗口标题变化了，更新标题和域名
            self.window_title = window_title
            self.window_hash = hashlib.sha256(window_title.encode('utf-8')).hexdigest()[:16]
            self.domain = self._extract_domain()
        self.switch_count += 1


class WindowMonitor:
    """窗口活动监测器"""

    def __init__(self, poll_interval: float = 1.0):
        """
        初始化窗口监测器
        :param poll_interval: 轮询间隔（秒），默认1秒，CPU占用<0.1%
        """
        self.poll_interval = poll_interval
        self.running = False
        self.paused = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.current_activity: Optional[WindowActivity] = None
        self.activities: Dict[str, WindowActivity] = {}  # window_hash -> WindowActivity
        self.session_start_time: Optional[float] = None
        self.session_end_time: Optional[float] = None

        # 分心检测
        self.distraction_checker: Optional[Callable[[str, str], bool]] = None
        self.on_distraction: Optional[Callable[[str, str, str], None]] = None
        self._distraction_cooldown: Dict[str, float] = {}
        self._distraction_cooldown_sec = 30  # 同一来源 30 秒内不重复提醒

    def _get_foreground_window_info(self) -> tuple[str, str, str]:
        """
        获取前台窗口信息
        :return: (应用名称, 窗口标题, 窗口标题哈希值)
        """
        if not WINDOWS_SUPPORT:
            return "unknown", "unknown", "unknown"

        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "unknown", "unknown", "unknown"

            # 获取进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            # 获取进程名称
            try:
                process = psutil.Process(pid)
                app_name = process.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = "unknown"

            # 获取窗口标题并计算哈希
            try:
                window_title = win32gui.GetWindowText(hwnd)
                if not window_title:
                    window_title = "(无标题)"
                # 计算SHA256哈希，仅用于识别相同窗口
                window_hash = hashlib.sha256(window_title.encode('utf-8')).hexdigest()[:16]
            except:
                window_title = "unknown"
                window_hash = "unknown"

            return app_name, window_title, window_hash

        except Exception as e:
            print(f"获取窗口信息失败: {e}")
            return "unknown", "unknown", "unknown"

    def _monitor_loop(self):
        """监测主循环"""
        while self.running:
            if not self.paused:
                timestamp = time.time()
                app_name, window_title, window_hash = self._get_foreground_window_info()

                # 分心实时检测（窗口切换时检查一次）
                if self.distraction_checker and self.on_distraction:
                    self._check_distraction(app_name, window_title, timestamp)

                # 窗口变化时更新记录
                if self.current_activity is None or self.current_activity.window_hash != window_hash:
                    # 结束当前活动
                    if self.current_activity is not None:
                        self.current_activity.update(timestamp, window_title)

                    # 新窗口活动
                    if window_hash in self.activities:
                        # 已有记录，更新
                        self.activities[window_hash].update(timestamp, window_title)
                        self.current_activity = self.activities[window_hash]
                    else:
                        # 新记录
                        new_activity = WindowActivity(app_name, window_title, window_hash, timestamp)
                        self.activities[window_hash] = new_activity
                        self.current_activity = new_activity
                else:
                    # 同一窗口，更新持续时间
                    self.current_activity.duration += self.poll_interval
                    self.current_activity.last_seen = timestamp
                    # 即使标题没变哈希也可能因为窗口切换而不同，所以这里检查一下标题是否变化
                    if window_title != self.current_activity.window_title:
                        self.current_activity.window_title = window_title
                        self.current_activity.domain = self.current_activity._extract_domain()

            time.sleep(self.poll_interval)

    def _check_distraction(self, app_name: str, window_title: str, timestamp: float):
        """检查当前窗口是否为分心窗口，若命中则触发回调（带冷却）"""
        if not self.distraction_checker or not self.on_distraction:
            return
        domain = _extract_domain_from_title(window_title)
        if not self.distraction_checker(app_name, domain):
            return

        key = domain if domain else app_name.lower()
        last_alert = self._distraction_cooldown.get(key, 0)
        if timestamp - last_alert < self._distraction_cooldown_sec:
            return

        self._distraction_cooldown[key] = timestamp
        self.on_distraction(app_name, domain, window_title)

    def start(self):
        """开始监测"""
        if not WINDOWS_SUPPORT:
            print("当前系统不支持窗口监测")
            return False

        if self.running:
            return True

        self.running = True
        self.paused = False
        self.activities.clear()
        self.current_activity = None
        self.session_start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("窗口监测已启动")
        return True

    def stop(self) -> List[dict]:
        """
        停止监测并返回活动记录
        :return: 活动记录列表
        """
        if not self.running:
            return []

        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

        self.session_end_time = time.time()

        # 结束最后一个活动
        if self.current_activity:
            self.current_activity.update(self.session_end_time)

        # 转换为字典格式返回
        result = []
        for activity in self.activities.values():
            result.append({
                "app_name": activity.app_name,
                "window_title": activity.window_title,
                "window_hash": activity.window_hash,
                "domain": activity.domain,
                "duration": round(activity.duration / 60, 1),  # 转换为分钟，保留1位小数
                "first_seen": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(activity.first_seen)),
                "last_seen": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(activity.last_seen)),
                "switch_count": activity.switch_count,
                "window_category": "",
                "user_custom_category": "",
                "is_distracting": None,
                "user_notes": ""
            })

        # 按时长降序排序
        result.sort(key=lambda x: x["duration"], reverse=True)
        print(f"窗口监测已停止，共记录 {len(result)} 条活动")
        return result

    def pause(self):
        """暂停监测"""
        if self.running and not self.paused:
            self.paused = True
            # 结束当前活动
            if self.current_activity:
                self.current_activity.update(time.time())
            print("窗口监测已暂停")

    def resume(self):
        """恢复监测"""
        if self.running and self.paused:
            self.paused = False
            # 重置当前活动，重新开始计时
            self.current_activity = None
            print("窗口监测已恢复")

    def is_running(self) -> bool:
        """是否正在监测"""
        return self.running and not self.paused

    def get_session_duration(self) -> float:
        """获取会话总时长（分钟）"""
        if self.session_start_time and self.session_end_time:
            return round((self.session_end_time - self.session_start_time) / 60, 1)
        return 0
