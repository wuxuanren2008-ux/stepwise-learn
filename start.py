# -*- coding: utf-8 -*-
"""一键启动：python -X utf8 start.py [--port 8765]"""
from __future__ import annotations

import argparse
import os
import sys
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    from server import BRAIN, DB_PATH, Handler
    from http.server import ThreadingHTTPServer

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1] if args.port == 0 else args.port
    if args.port == 0:
        url = f"http://127.0.0.1:{port}/"
    else:
        # 指定端口被占用/被系统保留时，自动退到系统分配端口
        try:
            srv.server_close()
            srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
            url = f"http://127.0.0.1:{args.port}/"
        except OSError:
            srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            url = f"http://127.0.0.1:{srv.server_address[1]}/"

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
