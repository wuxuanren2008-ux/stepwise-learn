# -*- coding: utf-8 -*-
"""本地 HTTP 服务：JSON API + 单页前端。仅监听 127.0.0.1，零第三方依赖。"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import get_brain                    # noqa: E402
from curriculum import all_topic_ids, list_courses  # noqa: E402
from pedagogy import Session                  # noqa: E402
from store import Store                       # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(ROOT, "static")
DB_PATH = os.path.join(ROOT, "data", "learn.db")

SESSIONS: dict[str, Session] = {}
STORE = Store(DB_PATH)
BRAIN = get_brain()


def frame_error(msg: str, code: str = "bad_request") -> dict:
    return {"error": code, "message": msg}


class Handler(BaseHTTPRequestHandler):
    server_version = "StepwiseLearn/1.0"

    def log_message(self, fmt, *args):
        # 只记录方法与路径，绝不记录 body（可能含凭据）
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    # ---------- 基础 ----------
    def _send(self, status: int, body: bytes, ctype: str, extra: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n <= 0:
            return {}
        raw = self.rfile.read(min(n, 64 * 1024))
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # ---------- 路由 ----------
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self._serve_static("index.html")
        if path.startswith("/static/"):
            return self._serve_static(path[len("/static/"):])
        if path == "/api/courses":
            return self._json(200, {
                "courses": list_courses(),
                "progress": STORE.progress(),
                "due_reviews": STORE.due_reviews(),
                "upcoming": STORE.upcoming_reviews(),
            })
        if path == "/api/config":
            return self._json(200, {
                "mode": BRAIN.mode,
                "api_enabled": BRAIN.mode == "api",
                "topic_count": len(all_topic_ids()),
                "db": "data/learn.db",
            })
        if path == "/api/progress":
            return self._json(200, {
                "progress": STORE.progress(),
                "due_reviews": STORE.due_reviews(),
                "upcoming": STORE.upcoming_reviews(),
                "mastery": {t: STORE.get_mastery(t) for t in all_topic_ids()},
            })
        if path == "/health":
            return self._json(200, {"ok": True, "mode": BRAIN.mode})
        return self._json(404, frame_error("not found", "not_found"))

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        try:
            if path == "/api/start":
                topic_id = str(body.get("topic_id", "")).strip()
                try:
                    s = Session(topic_id, BRAIN, STORE)
                except ValueError:
                    return self._json(400, frame_error("unknown topic_id"))
                SESSIONS[s.id] = s
                return self._json(200, s.advance("start"))

            if path == "/api/action":
                sid = str(body.get("session_id", "")).strip()
                s = SESSIONS.get(sid)
                if s is None:
                    return self._json(404, frame_error("session not found", "no_session"))
                action = str(body.get("action", "")).strip()
                frame = s.advance(action, body.get("payload") or {})
                return self._json(200, frame)

            if path == "/api/review":
                topic_id = str(body.get("topic_id", "")).strip()
                if topic_id not in all_topic_ids():
                    return self._json(400, frame_error("unknown topic_id"))
                correct = bool(body.get("correct", True))
                STORE.record_attempt(topic_id, correct, 0 if correct else 0)
                due = STORE.schedule_review(topic_id, correct=correct)
                return self._json(200, {"ok": True, "topic_id": topic_id,
                                       "correct": correct, "due_at": due,
                                       "interval_days": STORE.get_mastery(topic_id)["interval_days"]})

            if path == "/api/reset":
                SESSIONS.clear()
                STORE.reset()
                return self._json(200, {"ok": True, "message": "本地进度已清空"})

            return self._json(404, frame_error("not found", "not_found"))
        except Exception as e:                       # 不让任何异常打挂服务
            traceback.print_exc()
            return self._json(500, frame_error(f"internal error: {type(e).__name__}", "internal"))

    def _serve_static(self, rel: str):
        rel = rel.replace("\\", "/").lstrip("/")
        if ".." in rel.split("/"):
            return self._json(403, frame_error("forbidden", "forbidden"))
        p = os.path.join(STATIC, rel)
        if not os.path.isfile(p):
            return self._json(404, frame_error("not found", "not_found"))
        ctype = mimetypes.guess_type(p)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        with open(p, "rb") as f:
            self._send(200, f.read(), ctype)


def main():
    ap = argparse.ArgumentParser(description="Stepwise Learn 本地学习应用")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Stepwise Learn 已启动: http://{args.host}:{args.port}/")
    print(f"模式: {BRAIN.mode}  |  数据: {DB_PATH}")
    print("Ctrl+C 停止")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        srv.shutdown()


if __name__ == "__main__":
    main()
