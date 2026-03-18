#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 配置管理模块
用于管理应用的各种设置参数
"""

import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "focus_time": 40,  # 专注时间（分钟）
    "break_time": 5,   # 休息时间（分钟）
    "min_interval": 5, # 最小间隔（分钟）
    "max_interval": 40, # 最大间隔（分钟）
    "micro_break": 60,  # 微休息时间（秒）
    "break_countdown": True,  # 是否显示休息倒计时
    "alert_count": 1,  # 提示音次数
    "volume": 0.5,  # 提示音音量 (0.0 - 1.0)
    "white_noise_volume": 0.5,  # 白噪音音量 (0.0 - 1.0)
    "white_noise_type": "forest"  # 白噪音类型: "forest" 或 "thunderstorm"
}


class ConfigManager:
    """配置管理类"""

    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 合并默认配置（处理新增配置项）
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
            else:
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"加载配置失败: {e}")
            return DEFAULT_CONFIG.copy()

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def get(self, key):
        """获取配置项"""
        return self.config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        """设置配置项"""
        if key in DEFAULT_CONFIG:
            # 验证数据类型
            expected_type = type(DEFAULT_CONFIG[key])
            if isinstance(value, expected_type):
                # 特殊验证：最大间隔不能超过专注时间
                if key == "max_interval":
                    if value > self.config.get("focus_time", 40):
                        raise ValueError("最大间隔不能超过专注时间")
                if key == "focus_time":
                    if self.config.get("max_interval", 40) > value:
                        self.config["max_interval"] = value
                self.config[key] = value
                return True
        return False

    def get_all(self):
        """获取所有配置"""
        return self.config.copy()

    def reset_to_default(self):
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        self.save_config()
