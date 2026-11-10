# -*- coding: utf-8 -*-
"""端到端自检：覆盖计划里的六条 Review Focus。零第三方依赖。"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain import OfflineBrain          # noqa: E402
from curriculum import all_topic_ids, get_topic  # noqa: E402
from pedagogy import Session           # noqa: E402
from store import Store                # noqa: E402

OK, FAIL = [], []


def check(name, cond, detail=""):
    (OK if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")


def post(base, path, obj):
    req = urllib.request.Request(
        base + path, data=json.dumps(obj).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        # 4xx 是服务端预期行为，仍要能读到 JSON 错误体
        return json.loads(e.read().decode())


def get(base, path):
    with urllib.request.urlopen(base + path, timeout=5) as r:
        return json.loads(r.read().decode())


def main():
    print("=" * 68)
    print("Stepwise Learn 自检")
    print("=" * 68)
    tmp = tempfile.mkdtemp(prefix="stepwise-")
    store = Store(os.path.join(tmp, "learn.db"))
    brain = OfflineBrain()
    tid = "chain-rule"
    topic = get_topic(tid)

    # 1) 离线可用 + 四阶段完整
    s = Session(tid, brain, store)
    f = s.advance("start")
    check("离线模式", brain.mode == "offline", f"mode={brain.mode}")
    check("hint 阶段", f["phase"] == "hint")
    check("提示阶段白板为空", len(f["board"]) == 0)

    # 2) 提示不泄答案
    leak = any(st["board"] in f["narration"] or st["say"] in f["narration"]
               for st in topic["steps"])
    check("提示不泄答案", not leak)
    f2 = s.advance("hint")
    leak2 = any(st["board"] in f2["narration"] or st["say"] in f2["narration"]
                for st in topic["steps"])
    check("追问提示仍不泄答案", not leak2)

    # 走到检查站
    phases = {f["phase"]}
    for _ in range(len(topic["steps"]) + 1):
        f = s.advance("reveal")
        phases.add(f["phase"])
    check("白板逐步揭示", f["step_index"] == len(topic["steps"]),
          f"step_index={f['step_index']}")
    check("进入检查站", f["phase"] == "checkpoint", f"phase={f['phase']}")
    check("演练阶段存在", "walkthrough" in phases)

    # 3) 答错回退 + 标记错步
    cp = topic["checkpoint"]
    wrong = (cp["answer"] + 1) % len(cp["options"])
    fw = s.advance("answer", {"index": wrong})
    check("答错仍留在检查站", fw["phase"] == "checkpoint")
    check("答错记录错步", len(fw["mastery"]["wrong_steps"]) > 0,
          f"wrong_steps={fw['mastery']['wrong_steps']}")
    check("答错回退到对应步骤", fw["step_index"] <= cp["wrong_step"] + 1,
          f"step_index={fw['step_index']} wrong_step={cp['wrong_step']}")

    # 答对 → 测验 → 掌握
    fc = s.advance("answer", {"index": cp["answer"]})
    check("答对进入测验", fc["phase"] == "quiz")
    for q in topic["quiz"]:
        fq = s.advance("quiz_answer", {"index": q["answer"]})
    check("测验完成进入掌握", fq["phase"] == "mastered", f"phase={fq['phase']}")
    check("掌握度写入", store.get_mastery(tid)["mastered"] == 1)

    # 4) 复习调度
    due = store.upcoming_reviews()
    check("复习排队", len(due) == 1, f"upcoming={len(due)}")
    check("到期时间在未来", due and due[0]["due_at"] > time.time())
    d1 = store.get_mastery(tid)["interval_days"]
    store.schedule_review(tid, correct=True)
    d2 = store.get_mastery(tid)["interval_days"]
    check("答对推进间隔", d2 >= d1, f"{d1} -> {d2}")
    store.schedule_review(tid, correct=False)
    d3 = store.get_mastery(tid)["interval_days"]
    check("答错重置为 1 天", d3 == 1, f"interval={d3}")

    # 5) 幂等：重复 start 不产生重复掌握度
    before = store.progress()["topics_started"]
    s.advance("start")
    after = store.progress()["topics_started"]
    check("重复 start 幂等", before == after, f"{before} -> {after}")

    # 6) 凭据不外泄（把 key 放进环境变量，验证响应里没有）
    os.environ["LEARN_API_KEY"] = "SK-TEST-DO-NOT-LEAK"
    from server import Handler  # noqa: F401  仅验证模块可导入
    check("server 模块可导入", True)

    # ---- 起真实服务打 API ----
    from http.server import ThreadingHTTPServer
    import server
    server.STORE = store
    server.SESSIONS = {}
    server.BRAIN = brain
    server.Handler.log_message = lambda *a, **k: None  # 自检期间静音访问日志
    srv = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
    port = srv.server_address[1]   # 让系统分配空闲端口，避开 Windows 保留端口段
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    base = f"http://127.0.0.1:{port}"
    try:
        cfg = get(base, "/api/config")
        check("GET /api/config", cfg["mode"] == "offline", f"mode={cfg['mode']}")
        courses = get(base, "/api/courses")
        check("GET /api/courses 含三门课", len(courses["courses"]) == 3,
              f"courses={len(courses['courses'])}")
        st = post(base, "/api/start", {"topic_id": "thesis-statement"})
        check("POST /api/start", st.get("phase") == "hint")
        r = post(base, "/api/action", {"session_id": st["session_id"], "action": "hint"})
        check("POST /api/action hint", r.get("phase") == "hint")
        body = json.dumps(r, ensure_ascii=False)
        check("响应不含 API key", "SK-TEST-DO-NOT-LEAK" not in body)
        bad = post(base, "/api/start", {"topic_id": "no-such-topic"})
        check("未知知识点返回 400 语义", "error" in bad)
        p = get(base, "/api/progress")
        check("GET /api/progress", "progress" in p)
        h = get(base, "/health")
        check("GET /health", h.get("ok") is True)
    finally:
        srv.shutdown()
        srv.server_close()
        os.environ.pop("LEARN_API_KEY", None)

    print("-" * 68)
    print(f"结果: {len(OK)} 通过 / {len(FAIL)} 失败")
    if FAIL:
        print("失败项:", ", ".join(FAIL))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
