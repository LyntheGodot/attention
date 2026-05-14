#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - PC-手机配对管理模块
生成/验证配对 token，管理配对状态
"""

import json
import os
import secrets
import socket
import time
from typing import Dict


PAIRING_FILE = "pairing.json"


def _get_pairing_path() -> str:
    utils_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(utils_dir), PAIRING_FILE)


def _get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except (OSError, socket.error):
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.error:
            return "127.0.0.1"


class PairingManager:
    """PC-手机配对管理器"""

    def __init__(self):
        self._data: Dict = {}
        self._load()

    def _load(self):
        path = _get_pairing_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                self._data = self._default_data()
        except (json.JSONDecodeError, IOError):
            self._data = self._default_data()

    def _save(self):
        path = _get_pairing_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _default_data() -> Dict:
        return {
            "token": "", "paired": False, "device_name": "",
            "paired_at": "", "local_ip": "", "udp_port": 56789,
            "http_port": 56790,
        }

    def generate_pairing(self, udp_port: int = 56789, http_port: int = 56790) -> Dict:
        local_ip = _get_local_ip()
        token = secrets.token_hex(16)
        self._data.update({
            "paired": False, "device_name": "", "paired_at": "",
            "local_ip": local_ip, "udp_port": udp_port,
            "http_port": http_port, "token": token,
        })
        self._save()
        return self.get_pairing_data()

    def get_pairing_data(self) -> Dict:
        return {
            "ip": self._data["local_ip"],
            "udp_port": self._data["udp_port"],
            "http_port": self._data["http_port"],
            "token": self._data["token"],
        }

    def get_qr_json_string(self) -> str:
        return json.dumps(self.get_pairing_data(), ensure_ascii=False)

    def confirm_pairing(self, device_name: str = "Android"):
        self._data["paired"] = True
        self._data["device_name"] = device_name
        self._data["paired_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        self._save()

    def verify_token(self, token: str) -> bool:
        return self._data["paired"] and self._data["token"] == token

    def is_paired(self) -> bool:
        return self._data.get("paired", False)

    def get_token(self) -> str:
        return self._data.get("token", "")

    def get_device_name(self) -> str:
        return self._data.get("device_name", "")

    def get_local_ip(self) -> str:
        return self._data.get("local_ip", "127.0.0.1")

    def get_udp_port(self) -> int:
        return self._data.get("udp_port", 56789)

    def get_http_port(self) -> int:
        return self._data.get("http_port", 56790)

    def unpair(self):
        self._data["paired"] = False
        self._data["device_name"] = ""
        self._data["paired_at"] = ""
        self._save()
