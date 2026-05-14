#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番茄钟应用 - HTTP 接收服务模块
PC 端启动轻量 HTTP 服务器，接收手机端回传的 App 使用数据
"""

import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Callable, Dict, List

DEFAULT_HTTP_PORT = 56790


class _ReportHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器（每个请求在新线程中处理）"""

    receiver_instance: Optional["HttpReceiver"] = None

    def do_POST(self):
        if self.path == "/report" and self.receiver_instance:
            self.receiver_instance._handle_report(self)
        elif self.path == "/pair_confirm" and self.receiver_instance:
            self.receiver_instance._handle_pair_confirm(self)
        elif self.path == "/ping":
            self._send_json(200, {"status": "ok", "server": "attention-pc"})
        else:
            self._send_json(404, {"error": "not found"})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/ping" or self.path == "/":
            self._send_json(200, {"status": "ok", "server": "attention-pc"})
        elif self.path == "/session_status" and self.receiver_instance:
            self._send_json(200, self.receiver_instance._get_session_status())
        else:
            self._send_json(404, {"error": "not found"})

    def _send_json(self, code: int, data: dict):
        self.send_response(code)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]}")


class HttpReceiver:
    """HTTP 接收服务器——接收手机端回传的使用数据"""

    def __init__(self, port: int = DEFAULT_HTTP_PORT):
        self.port = port
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self.on_report: Optional[Callable[[Dict], None]] = None
        self.on_pair_confirm: Optional[Callable[[str], bool]] = None
        self._phone_reports: List[Dict] = []
        self._session_status = "idle"
        self._session_id = ""
        _ReportHandler.receiver_instance = self

    def start(self) -> bool:
        if self._running:
            return True
        try:
            self._server = HTTPServer(("0.0.0.0", self.port), _ReportHandler)
            self._server.timeout = 0.5
            self._running = True
            self._thread = threading.Thread(target=self._serve, daemon=True)
            self._thread.start()
            print(f"HTTP 接收服务已启动 → 0.0.0.0:{self.port}")
            return True
        except OSError as e:
            print(f"启动 HTTP 接收服务失败: {e}")
            return False

    def stop(self):
        self._running = False
        self._server = None
        self._thread = None
        print("HTTP 接收服务已停止")

    def _serve(self):
        while self._running and self._server:
            try:
                self._server.handle_request()
            except Exception:
                if not self._running:
                    break

    def _handle_pair_confirm(self, handler: _ReportHandler):
        try:
            content_length = int(handler.headers.get("Content-Length", 0))
            body = handler.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
            token = data.get("token", "")
            device_name = data.get("device_name", "Android")
            if self.on_pair_confirm:
                ok = self.on_pair_confirm(token, device_name)
                if ok:
                    handler._send_json(200, {"status": "paired", "device": device_name})
                    return
            handler._send_json(403, {"error": "pairing rejected"})
        except Exception as e:
            handler._send_json(400, {"error": str(e)})

    def _handle_report(self, handler: _ReportHandler):
        try:
            content_length = int(handler.headers.get("Content-Length", 0))
            body = handler.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
            phone_activities = data.get("activities", [])
            token = data.get("token", "")
            if self.on_report:
                verified = self.on_report(data)
                if not verified:
                    handler._send_json(403, {"error": "invalid token"})
                    return
            self._phone_reports.append(data)
            handler._send_json(200, {
                "status": "ok",
                "received": len(phone_activities),
            })
            print(f"收到手机报告: {len(phone_activities)} 条活动记录")
        except (json.JSONDecodeError, ValueError) as e:
            handler._send_json(400, {"error": f"invalid json: {e}"})
        except Exception as e:
            print(f"处理手机报告失败: {e}")
            handler._send_json(500, {"error": str(e)})

    def _get_session_status(self) -> Dict:
        return {
            "status": self._session_status,
            "session_id": self._session_id,
        }

    def set_session_active(self, session_id: str):
        self._session_status = "active"
        self._session_id = session_id
        self._phone_reports.clear()

    def set_session_stopped(self):
        self._session_status = "stopped"

    def set_session_idle(self):
        self._session_status = "idle"
        self._session_id = ""

    def get_pending_reports(self) -> List[Dict]:
        reports = self._phone_reports.copy()
        self._phone_reports.clear()
        return reports

    def is_running(self) -> bool:
        return self._running
