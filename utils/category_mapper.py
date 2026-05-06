#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 分类映射管理器
用于管理应用程序到分类的映射关系，自动推荐分类
"""

import json
import os
from typing import Dict, List, Optional


class CategoryMapper:
    """分类映射管理器"""

    # 预设分类
    DEFAULT_CATEGORIES = [
        "📝 工作",
        "📚 学习",
        "💬 社交",
        "🎮 娱乐",
        "🔍 浏览",
        "✨ 其他"
    ]

    def __init__(self, mapping_file: str = None):
        """
        初始化分类映射管理器
        :param mapping_file: 映射文件路径，默认使用项目根目录下的 category_mapping.json
        """
        if mapping_file is None:
            # 默认存储路径
            utils_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(utils_dir)
            self.mapping_file = os.path.join(project_root, "category_mapping.json")
        else:
            self.mapping_file = mapping_file

        self.app_mapping: Dict[str, str] = {}  # app_name -> category
        self.custom_categories: List[str] = []
        self._load_mapping()

    def _load_mapping(self):
        """从文件加载映射关系和自定义分类"""
        if not os.path.exists(self.mapping_file):
            # 初始化默认配置
            self.app_mapping = {}
            self.custom_categories = self.DEFAULT_CATEGORIES.copy()
            self._save_mapping()
            return

        try:
            with open(self.mapping_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.app_mapping = data.get("app_mapping", {})
                self.custom_categories = data.get("categories", self.DEFAULT_CATEGORIES.copy())

            # 确保预设分类都存在
            for cat in self.DEFAULT_CATEGORIES:
                if cat not in self.custom_categories:
                    self.custom_categories.append(cat)

        except Exception as e:
            print(f"加载分类映射失败: {e}")
            self.app_mapping = {}
            self.custom_categories = self.DEFAULT_CATEGORIES.copy()

    def _save_mapping(self):
        """保存映射关系和分类到文件"""
        try:
            data = {
                "app_mapping": self.app_mapping,
                "categories": self.custom_categories
            }
            with open(self.mapping_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分类映射失败: {e}")

    def get_recommended_category(self, identifier: str) -> Optional[str]:
        """
        根据应用名称或域名获取推荐分类
        :param identifier: 应用程序名称（如 chrome.exe）或域名（如 github.com）
        :return: 推荐的分类，没有则返回None
        """
        identifier_lower = identifier.lower()
        return self.app_mapping.get(identifier_lower)

    def add_mapping(self, app_name: str, category: str):
        """
        添加应用到分类的映射
        :param app_name: 应用程序名称
        :param category: 分类名称
        """
        app_name_lower = app_name.lower()
        self.app_mapping[app_name_lower] = category
        self._save_mapping()

    def add_custom_category(self, category: str) -> bool:
        """
        添加新的自定义分类
        :param category: 分类名称
        :return: 是否添加成功（已存在则返回False）
        """
        if category not in self.custom_categories:
            self.custom_categories.append(category)
            self._save_mapping()
            return True
        return False

    def delete_category(self, category: str) -> bool:
        """
        删除分类
        :param category: 分类名称
        :return: 是否删除成功（预设分类不能删除）
        """
        if category in self.DEFAULT_CATEGORIES:
            return False  # 预设分类不能删除
        if category in self.custom_categories:
            self.custom_categories.remove(category)
            # 将使用该分类的映射改为"其他"
            other_category = next(cat for cat in self.DEFAULT_CATEGORIES if "其他" in cat)
            for app, cat in self.app_mapping.items():
                if cat == category:
                    self.app_mapping[app] = other_category
            self._save_mapping()
            return True
        return False

    def rename_category(self, old_category: str, new_category: str) -> bool:
        """
        重命名分类
        :param old_category: 旧分类名称
        :param new_category: 新分类名称
        :return: 是否重命名成功
        """
        if old_category in self.DEFAULT_CATEGORIES:
            return False  # 预设分类不能重命名
        if old_category in self.custom_categories and new_category not in self.custom_categories:
            idx = self.custom_categories.index(old_category)
            self.custom_categories[idx] = new_category
            # 更新所有使用该分类的映射
            for app, cat in self.app_mapping.items():
                if cat == old_category:
                    self.app_mapping[app] = new_category
            self._save_mapping()
            return True
        return False

    def get_all_categories(self) -> List[str]:
        """获取所有分类列表"""
        return self.custom_categories.copy()

    def get_most_used_categories(self, limit: int = 5) -> List[str]:
        """
        获取最常用的分类（按使用频率排序）
        :param limit: 返回数量
        :return: 分类列表
        """
        if not self.app_mapping:
            return self.DEFAULT_CATEGORIES[:limit]

        # 统计使用频率
        category_count: Dict[str, int] = {}
        for cat in self.app_mapping.values():
            category_count[cat] = category_count.get(cat, 0) + 1

        # 按频率排序
        sorted_categories = sorted(category_count.items(), key=lambda x: x[1], reverse=True)
        result = [cat for cat, _ in sorted_categories]

        # 补全预设分类
        for cat in self.DEFAULT_CATEGORIES:
            if cat not in result:
                result.append(cat)

        return result[:limit]

    def batch_update_mappings(self, mappings: Dict[str, str]):
        """
        批量更新映射关系
        :param mappings: app_name -> category 的字典
        """
        for app, cat in mappings.items():
            self.app_mapping[app.lower()] = cat
        self._save_mapping()

    def clear_mappings(self):
        """清空所有映射关系"""
        self.app_mapping.clear()
        self._save_mapping()
