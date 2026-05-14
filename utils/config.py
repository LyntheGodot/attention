#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 配置管理模块
"""

import json
import os
import sys

CONFIG_FILE = "config.json"


def _get_user_data_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        exe_path = os.path.dirname(sys.executable)
        return exe_path
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(utils_dir)


def _get_config_path():
    base_path = _get_user_data_path()
    return os.path.join(base_path, CONFIG_FILE)


DEFAULT_CONFIG = {
    "focus_time": 40,
    "break_time": 5,
    "min_interval": 5,
    "max_interval": 40,
    "micro_break": 60,
    "break_countdown": True,
    "alert_count": 1,
    "volume": 0.5,
    "white_noise_volume": 0.5,
    "white_noise_type": "forest",
    "window_monitoring_enabled": True,
    "phone_pairing_enabled": False,
    "phone_udp_port": 56789,
    "phone_http_port": 56790,
}


class ConfigManager:
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        path = _get_config_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._config.update(saved)
        except (json.JSONDecodeError, IOError):
            pass

    def save_config(self):
        path = _get_config_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=4)

    def get(self, key, default=None):
        return self._config.get(key, default)

    def get_all(self):
        return self._config.copy()

    def set(self, key, value):
        self._config[key] = value
