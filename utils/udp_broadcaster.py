#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - UDP 广播模块
向局域网广播专注会话状态变更
"""

import json
import socket
from typing import Optional

DEFAULT_UDP_PORT = 56789
BROADCAST_ADDR = "255.255.255.255"


class UdpBroadcaster:
    """UDP 广播器——向局域网通知会话状态"""

    def __init__(self, port: int = DEFAULT_UDP_PORT):
        self.port = port
        self._socket: Optional[socket.socket] = None
        self._enabled = True
        self._init_socket()

    def _init_socket(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as e:
            print(f"UDP socket 初始化失败: {e}")
            self._socket = None

    def broadcast(self, message: dict) -> bool:
        if not self._enabled or self._socket is None:
            return False
        try:
            data = json.dumps(message, ensure_ascii=False).encode("utf-8")
            self._socket.sendto(data, (BROADCAST_ADDR, self.port))
            print(f"UDP 广播已发送: {message.get('type', '?')} → {self.port}")
            return True
        except OSError as e:
            print(f"UDP 广播失败: {e}")
            return False

    def notify_session_start(self, session_id: str, token: str) -> bool:
        return self.broadcast({
            "type": "SESSION_START",
            "session_id": session_id,
            "token": token,
            "timestamp": int(__import__('time').time()),
        })

    def notify_session_stop(self, session_id: str, token: str) -> bool:
        return self.broadcast({
            "type": "SESSION_STOP",
            "session_id": session_id,
            "token": token,
            "timestamp": int(__import__('time').time()),
        })

    def set_enabled(self, enabled: bool):
        self._enabled = enabled

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None
