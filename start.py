# -*- coding: utf-8 -*-
"""一键启动：python -X utf8 start.py [--port 8765] [--no-browser]

端口策略：优先绑定 --port；被占用或属于系统保留段时，自动改用系统分配的空闲端口。
"""
from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from http.server import ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import BRAIN, DB_PATH, Handler  # noqa: E402


def bind(preferred: int | None):
    """返回 (server, url)。preferred=None 表示直接让系统分配。"""
    if preferred:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", preferred), Handler)
            return srv, f"http://127.0.0.1:{preferred}/"
        except OSError:
            pass
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def main():
    ap = argparse.ArgumentParser(description="Stepwise Learn 本地学习应用")
    ap.add_argument("--port", type=int, default=8765,
                    help="首选端口，默认 8765；被占用时自动换端口。传 0 表示直接随机分配")
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    srv, url = bind(None if args.port == 0 else args.port)

    print("=" * 56)
    print("  Stepwise · 一步步带你学会")
    print("=" * 56)
    print(f"  打开: {url}")
    print(f"  模式: {BRAIN.mode}")
    print(f"  数据: {DB_PATH}（只存本机）")
    print("  停止: 按 Ctrl+C")
    print("=" * 56)
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        srv.shutdown()


if __name__ == "__main__":
    main()
