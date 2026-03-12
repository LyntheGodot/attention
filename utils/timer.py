#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 计时器功能模块
实现倒计时和随机提示功能
"""

import time
import threading
import random


class TimerState:
    """计时器状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    MICRO_BREAK = "micro_break"


class PomodoroTimer:
    """番茄钟计时器"""

    def __init__(self, focus_time=40, break_time=5, min_interval=5, max_interval=40, micro_break=60):
        self.focus_time = focus_time * 60  # 转换为秒
        self.break_time = break_time * 60
        self.min_interval = min_interval * 60
        self.max_interval = max_interval * 60
        self.micro_break = micro_break

        self.remaining_time = self.focus_time
        self.total_focus_time = self.focus_time
        self.state = TimerState.IDLE

        self.random_alert_time = None
        self.micro_break_remaining = 0
        self.paused_before_micro = 0

        self.timer_thread = None
        self.running = False

        self.on_tick = None
        self.on_complete = None
        self.on_random_alert = None
        self.on_micro_break_start = None
        self.on_micro_break_end = None

    def set_times(self, focus_time=None, break_time=None, min_interval=None, max_interval=None, micro_break=None):
        """设置时间参数"""
        if focus_time is not None:
            self.focus_time = focus_time * 60
            self.total_focus_time = self.focus_time
        if break_time is not None:
            self.break_time = break_time * 60
        if min_interval is not None:
            self.min_interval = min_interval * 60
        if max_interval is not None:
            self.max_interval = max_interval * 60
        if micro_break is not None:
            self.micro_break = micro_break

        if self.state == TimerState.IDLE:
            self.remaining_time = self.focus_time

    def start(self):
        """开始计时"""
        if self.state in (TimerState.IDLE, TimerState.PAUSED):
            self.state = TimerState.RUNNING
            self.running = True

            if self.random_alert_time is None:
                self._generate_random_alert()

            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()

    def pause(self):
        """暂停计时"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self.running = False

    def reset(self):
        """重置计时器"""
        self.state = TimerState.IDLE
        self.running = False
        self.remaining_time = self.focus_time
        self.random_alert_time = None
        self.micro_break_remaining = 0
        self.paused_before_micro = 0
        if self.on_tick:
            self.on_tick(self.remaining_time, self.total_focus_time)

    def _timer_loop(self):
        """计时循环"""
        while self.running and self.remaining_time > 0:
            if self.state == TimerState.RUNNING:
                time.sleep(0.1)
                self.remaining_time -= 0.1

                if self.random_alert_time is not None and self.remaining_time <= self.random_alert_time:
                    self._trigger_micro_break()
                    continue

                if self.on_tick:
                    self.on_tick(self.remaining_time, self.total_focus_time)

            elif self.state == TimerState.MICRO_BREAK:
                time.sleep(0.1)
                self.micro_break_remaining -= 0.1

                if self.micro_break_remaining <= 0:
                    self._end_micro_break()
                else:
                    if self.on_tick:
                        self.on_tick(self.micro_break_remaining, self.micro_break, is_micro_break=True)

        if self.running and self.remaining_time <= 0:
            self.state = TimerState.IDLE
            self.running = False
            if self.on_complete:
                self.on_complete()

    def _generate_random_alert(self):
        """生成随机提示时间点"""
        if self.min_interval < self.max_interval:
            elapsed = self.total_focus_time - self.remaining_time
            remaining = self.remaining_time

            min_time = max(self.min_interval, elapsed + 60)
            max_time = min(self.max_interval, elapsed + remaining - 60)

            if max_time > min_time:
                random_total = random.uniform(min_time, max_time)
                self.random_alert_time = self.total_focus_time - random_total

    def _trigger_micro_break(self):
        """触发微休息"""
        self.state = TimerState.MICRO_BREAK
        self.paused_before_micro = self.remaining_time
        self.micro_break_remaining = self.micro_break
        self.random_alert_time = None

        if self.on_random_alert:
            self.on_random_alert()
        if self.on_micro_break_start:
            self.on_micro_break_start()

    def _end_micro_break(self):
        """结束微休息"""
        self.state = TimerState.RUNNING
        self.micro_break_remaining = 0
        self._generate_random_alert()

        if self.on_micro_break_end:
            self.on_micro_break_end()

        if self.on_tick:
            self.on_tick(self.remaining_time, self.total_focus_time)

    def get_progress(self):
        """获取进度百分比"""
        if self.state == TimerState.MICRO_BREAK:
            return (self.micro_break - self.micro_break_remaining) / self.micro_break
        return (self.total_focus_time - self.remaining_time) / self.total_focus_time

    def get_remaining_text(self):
        """获取剩余时间文本"""
        if self.state == TimerState.MICRO_BREAK:
            seconds = max(0, int(self.micro_break_remaining))
        else:
            seconds = max(0, int(self.remaining_time))
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
