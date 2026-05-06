#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 分心行为黑名单模块
从用户标注数据中自动构建分心窗口黑名单，用于实时提醒
"""

import json
import os
from typing import Dict, Set, Optional


class DistractionBlacklist:
    """分心黑名单——从 activity_records.json 中自动学习用户标记的分心行为"""

    def __init__(self, storage_file: str = None):
        if storage_file is None:
            utils_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(utils_dir)
            self.storage_file = os.path.join(project_root, "activity_records.json")
        else:
            self.storage_file = storage_file

        self.app_names: Set[str] = set()
        self.domains: Set[str] = set()
        self._last_mtime: float = 0
        self.reload()

    def reload(self):
        """重新加载黑名单（用户标注后调用）"""
        self.app_names.clear()
        self.domains.clear()

        if not os.path.exists(self.storage_file):
            return

        try:
            mtime = os.path.getmtime(self.storage_file)
            if mtime == self._last_mtime:
                return
            self._last_mtime = mtime
        except OSError:
            return

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        for date_sessions in records.values():
            for session in date_sessions:
                for activity in session.get("activities", []):
                    if activity.get("is_distracting", False):
                        app = activity.get("app_name", "").lower()
                        domain = activity.get("domain", "").lower()
                        if domain:
                            # 有域名的分心行为：只按域名匹配，不把整个浏览器拉黑
                            self.domains.add(domain)
                        elif app and app != "unknown":
                            # 无域名的分心行为（原生应用）：按应用名匹配
                            self.app_names.add(app)

    def matches(self, app_name: str, domain: str) -> bool:
        """检查当前窗口是否命中黑名单（域名优先，应用名作为无域名时的兜底）"""
        if domain and domain.lower() in self.domains:
            return True
        if app_name.lower() in self.app_names:
            return True
        return False

    def size(self) -> int:
        """黑名单条目数"""
        return len(self.app_names) + len(self.domains)

    def get_all_entries(self) -> Dict[str, Set[str]]:
        return {"app_names": self.app_names.copy(), "domains": self.domains.copy()}
