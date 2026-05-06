#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 活动记录存储管理器
用于保存和查询窗口活动记录和用户标注数据
"""

import json
import os
import uuid
import time
from typing import Dict, List, Optional


class ActivityStorageManager:
    """活动记录存储管理器"""

    def __init__(self, storage_file: str = None):
        """
        初始化存储管理器
        :param storage_file: 存储文件路径，默认使用项目根目录下的 activity_records.json
        """
        if storage_file is None:
            # 默认存储路径
            utils_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(utils_dir)
            self.storage_file = os.path.join(project_root, "activity_records.json")
        else:
            self.storage_file = storage_file

        self.records: Dict[str, List[dict]] = self._load_records()

    def _load_records(self) -> Dict[str, List[dict]]:
        """从文件加载记录"""
        if not os.path.exists(self.storage_file):
            return {}

        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载活动记录失败: {e}")
            return {}

    def _save_records(self):
        """保存记录到文件"""
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            print(f"活动记录已保存到: {self.storage_file}")
        except Exception as e:
            print(f"保存活动记录失败: {e}")

    def add_session_record(self, activities: List[dict], focus_duration: int) -> str:
        """
        添加新的会话记录
        :param activities: 活动列表（来自WindowMonitor.stop()）
        :param focus_duration: 本次专注时长（分钟）
        :return: 新会话的ID
        """
        session_id = str(uuid.uuid4())
        today_str = time.strftime("%Y-%m-%d")
        now_str = time.strftime("%Y-%m-%dT%H:%M:%S")

        # 计算统计数据
        total_duration = sum(act["duration"] for act in activities)
        distraction_duration = sum(act["duration"] for act in activities if act.get("is_distracting", False))
        distraction_ratio = round(distraction_duration / total_duration, 2) if total_duration > 0 else 0
        total_switches = sum(act["switch_count"] for act in activities)

        # 计算平均专注时长
        if len(activities) > 0:
            average_focus_streak = round(total_duration / len(activities), 1)
        else:
            average_focus_streak = 0

        # 构造会话记录
        session_record = {
            "session_id": session_id,
            "start_time": activities[0]["first_seen"] if activities else now_str,
            "end_time": activities[-1]["last_seen"] if activities else now_str,
            "focus_duration": focus_duration,
            "session_goal": "",
            "overall_rating": 0,
            "activities": activities,  # 包含 window_title, domain 等完整信息
            "distraction_ratio": distraction_ratio,
            "total_switches": total_switches,
            "average_focus_streak": average_focus_streak
        }

        # 添加到记录中
        if today_str not in self.records:
            self.records[today_str] = []
        self.records[today_str].append(session_record)

        # 保存到文件
        self._save_records()

        return session_id

    def update_activity_label(self, session_id: str, activity_idx: int,
                             category: str = None, is_distracting: bool = None,
                             user_notes: str = None, custom_category: str = None) -> bool:
        """
        更新活动的标注信息
        :param session_id: 会话ID
        :param activity_idx: 活动在会话中的索引
        :param category: 分类（可选）
        :param is_distracting: 是否分心（可选）
        :param user_notes: 用户备注（可选）
        :param custom_category: 用户自定义分类（可选）
        :return: 是否更新成功
        """
        # 查找会话
        for date_records in self.records.values():
            for session in date_records:
                if session["session_id"] == session_id:
                    if 0 <= activity_idx < len(session["activities"]):
                        activity = session["activities"][activity_idx]
                        if category is not None:
                            activity["window_category"] = category
                        if is_distracting is not None:
                            activity["is_distracting"] = is_distracting
                        if user_notes is not None:
                            activity["user_notes"] = user_notes
                        if custom_category is not None:
                            activity["user_custom_category"] = custom_category

                        # 重新计算分心比例
                        total_duration = sum(act["duration"] for act in session["activities"])
                        distraction_duration = sum(act["duration"] for act in session["activities"] if act.get("is_distracting", False))
                        session["distraction_ratio"] = round(distraction_duration / total_duration, 2) if total_duration > 0 else 0

                        self._save_records()
                        return True
        return False

    def get_records_by_date(self, date_str: str) -> List[dict]:
        """
        获取指定日期的所有记录
        :param date_str: 日期字符串，格式 "YYYY-MM-DD"
        :return: 会话记录列表
        """
        return self.records.get(date_str, [])

    def get_all_records(self) -> Dict[str, List[dict]]:
        """获取所有记录"""
        return self.records.copy()

    def get_recent_records(self, days: int = 7) -> List[dict]:
        """
        获取最近N天的记录
        :param days: 天数
        :return: 会话记录列表，按时间倒序排列
        """
        import datetime
        result = []
        today = datetime.date.today()

        for i in range(days):
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            if date_str in self.records:
                result.extend(self.records[date_str])

        return result

    def delete_session(self, session_id: str) -> bool:
        """
        删除指定会话记录
        :param session_id: 会话ID
        :return: 是否删除成功
        """
        for date_str, date_records in self.records.items():
            for i, session in enumerate(date_records):
                if session["session_id"] == session_id:
                    del date_records[i]
                    if not date_records:
                        del self.records[date_str]
                    self._save_records()
                    return True
        return False

    def export_records(self, export_path: str) -> bool:
        """
        导出所有记录到指定文件
        :param export_path: 导出文件路径
        :return: 是否导出成功
        """
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出记录失败: {e}")
            return False

    def import_records(self, import_path: str, merge: bool = True) -> bool:
        """
        从文件导入记录
        :param import_path: 导入文件路径
        :param merge: 是否合并到现有记录，False会覆盖现有记录
        :return: 是否导入成功
        """
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                imported_records = json.load(f)

            if not merge:
                self.records = imported_records
            else:
                # 合并记录
                for date_str, sessions in imported_records.items():
                    if date_str not in self.records:
                        self.records[date_str] = []
                    self.records[date_str].extend(sessions)

            self._save_records()
            return True
        except Exception as e:
            print(f"导入记录失败: {e}")
            return False
