#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注意力番茄钟 - 主程序入口
一个帮助培养专注力的番茄钟应用
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
