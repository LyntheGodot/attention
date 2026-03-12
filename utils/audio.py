#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - 音频播放模块
用于播放提示音和音效（简化版）
"""

import os
import threading

# 尝试导入 pygame，不可用时使用系统蜂鸣声
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


class AudioPlayer:
    """音频播放器类（简化版）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式确保只有一个音频播放器实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化音频播放器（简化版）"""
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.mixer_initialized = False
        self._initialized = True

        if PYGAME_AVAILABLE:
            self._init_pygame_mixer()

    def _init_pygame_mixer(self):
        """初始化 pygame mixer（简化版）"""
        try:
            pygame.mixer.init()
            self.mixer_initialized = True
            print(f"音频系统初始化成功: {self.mixer_initialized}")
        except Exception as e:
            print(f"pygame 音频初始化失败: {e}")

    def play_sound(self, sound_file=None, volume=0.3):
        """播放音效（简化版）"""
        if self.mixer_initialized:
            try:
                if sound_file and os.path.exists(sound_file):
                    print(f"正在加载音效: {sound_file}")
                    sound = pygame.mixer.Sound(sound_file)
                    sound.set_volume(volume)
                    sound.play()
                    print("音效播放已触发器")
                else:
                    print(f"音效文件不存在: {sound_file}")
                    self._play_system_sound()
            except Exception as e:
                print(f"播放音效失败: {e}")
                import traceback
                traceback.print_exc()
                self._play_system_sound()
        else:
            print("音频系统未初始化，使用系统蜂鸣声")
            self._play_system_sound()

    def _play_system_sound(self):
        """播放系统蜂鸣声（备用方案）"""
        try:
            import winsound
            winsound.Beep(800, 500)
        except ImportError:
            try:
                import sys
                sys.stdout.write("\a")
                sys.stdout.flush()
            except:
                pass

    def play_notification(self, count=1):
        """播放通知提示音（使用 sound1.wav）"""
        # 获取项目根目录
        sound_file = self._get_sound_file_path()

        # 打印调试信息（帮助排查问题）
        print(f"尝试播放提示音: {sound_file}")
        print(f"文件是否存在: {os.path.exists(sound_file)}")

        # 根据count循环播放
        for i in range(count):
            thread = threading.Thread(target=self.play_sound, args=(sound_file, 0.3), daemon=True)
            thread.start()
            # 如果有多次播放，间隔0.5秒
            if i < count - 1:
                import time
                time.sleep(0.5)

    def _get_sound_file_path(self):
        """获取 sound1.wav 的绝对路径"""
        # 方法1: 从当前文件位置向上查找
        utils_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(utils_dir)
        sound_file = os.path.join(project_root, "lingsheng", "sound1.wav")
        sound_file = os.path.normpath(sound_file)

        if os.path.exists(sound_file):
            return sound_file

        # 方法2: 尝试从当前工作目录查找
        cwd = os.getcwd()
        sound_file_cwd = os.path.join(cwd, "lingsheng", "sound1.wav")
        if os.path.exists(sound_file_cwd):
            return os.path.normpath(sound_file_cwd)

        # 如果都找不到，返回方法1的路径用于调试
        print(f"找不到 sound1.wav，尝试过: {sound_file}, {sound_file_cwd}")
        return sound_file

    def cleanup(self):
        """清理资源（简化版）"""
        if self.mixer_initialized:
            try:
                pygame.mixer.quit()
                self.mixer_initialized = False
            except Exception as e:
                print(f"清理音频资源时出错: {e}")

    def __del__(self):
        """析构时清理资源"""
        self.cleanup()