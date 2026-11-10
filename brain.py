# -*- coding: utf-8 -*-
"""可插拔「大脑」：离线规则引擎（默认）+ OpenAI 兼容 API（可选，失败自动回退）。

接口：brain.mode / brain.narrate(kind, topic, ctx) -> str
凭据只从环境变量读取：LEARN_API_BASE / LEARN_API_KEY / LEARN_MODEL
绝不硬编码、绝不写入日志或响应。
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

OFFLINE_TEMPLATES = {
    "hint": (
        "先别看答案。{cue}\n\n"
        "我会一段一段带你看，但每一步之前你都可以先自己说一遍思路。"
        "目标：{goal}"
    ),
    "hint_again": (
        "换个角度：把题目里最让你犹豫的那个词圈出来，问自己「它到底在问什么」。\n\n"
        "{cue}\n\n"
        "想好一个猜测就可以看第一步——猜错也没关系，错的那一步正是我们要练的地方。"
    ),
    "reveal": (
        "第 {step_index} 步 · {board}\n\n{say}\n\n"
        "⚠ 常见的卡点：{misconception}。如果刚才你正好卡在这里，"
        "停 10 秒用自己的话复述一遍再继续。"
    ),
    "checkpoint": (
        "现在换我来问你（这一步你会反过来被考一次）：\n\n{question}\n\n"
        "先自己判断，再选。选错会带你回到对应的那一步。"
    ),
    "checkpoint_ok": (
        "对了。{why}\n\n"
        "接着两道小测，几天后还会再回来找你——那时候才算真的记住。"
    ),
    "checkpoint_wrong": (
        "这里最容易漏的是「{misconception}」。\n\n"
        "回到这一步：{board}\n{say}\n\n"
        "再看一遍正确思路：{why}\n\n想清楚后重新选。"
    ),
    "quiz_ok": "答对了。{why}\n\n还有一题。",
    "quiz_wrong": (
        "再看一眼：{why}\n\n"
        "不用急，想清楚再选；这次的错误会记进你的复习队列。"
    ),
    "mastered": (
        "这一节走完了 ✓ 你不是「看完了」，是「被问过、错过、再答对了」。\n\n"
        "我把它排进了复习队列，下次到期会在首页提醒你。"
        "真正拉开差距的是那次快要忘记时又被拉回来的复习。"
    ),
}


class OfflineBrain:
    """零依赖、零网络。用课程数据 + 苏格拉底式模板生成讲解。"""

    mode = "offline"

    def narrate(self, kind: str, topic: dict, ctx: dict) -> str:
        tpl = OFFLINE_TEMPLATES.get(kind, "{say}")
        data = {"goal": topic.get("goal", ""), "cue": topic.get("cue", ""), **ctx}
        try:
            return tpl.format(**data)
        except (KeyError, IndexError):
            return str(data.get("say") or data.get("why") or tpl)


class APIBrain:
    """OpenAI 兼容 /v1/chat/completions。任何异常都回退离线，不影响教学流程。"""

    mode = "api"

    def __init__(self, base: str, key: str, model: str, fallback: OfflineBrain):
        self.base = base.rstrip("/")
        self.key = key
        self.model = model
        self.fallback = fallback
        self.timeout = float(os.environ.get("LEARN_API_TIMEOUT", "12"))

    def narrate(self, kind: str, topic: dict, ctx: dict) -> str:
        offline = self.fallback.narrate(kind, topic, ctx)
        system = (
            "你是一位苏格拉底式导师，教留学生学习。规则："
            "1) 提示阶段只给方向，绝不给最终答案；"
            "2) 一次只讲一步，用中文，关键术语保留英文；"
            "3) 指出常见错步并要求学生自己复述；"
            "4) 不要输出 markdown 标题，控制在 120 字以内。"
        )
        user = (
            f"知识点：{topic['title']}\n目标：{topic['goal']}\n"
            f"阶段：{kind}\n上下文：{json.dumps(ctx, ensure_ascii=False)}\n"
            f"离线讲解（可参考但不要照抄）：{offline}"
        )
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
            "max_tokens": 300,
        }).encode("utf-8")
        req = urllib.request.Request(
            self.base + "/v1/chat/completions", data=body, method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = r.read().decode("utf-8", "replace")
            data = json.loads(raw)
            text = data["choices"][0]["message"]["content"].strip()
            if not text:
                return offline
            # 硬护栏：提示阶段不能出现任何尚未揭示的步骤内容
            if kind in ("hint", "hint_again"):
                for s in topic.get("steps", []):
                    if s["board"] in text or s["say"] in text:
                        return offline
            return text
        except (urllib.error.URLError, TimeoutError, KeyError,
                json.JSONDecodeError, OSError, ValueError):
            self.fallback.mode = "offline-fallback"
            return offline


def get_brain():
    """环境变量齐备则用 API，否则离线。API 不可达时自动回退。"""
    offline = OfflineBrain()
    base = os.environ.get("LEARN_API_BASE", "").strip()
    key = os.environ.get("LEARN_API_KEY", "").strip()
    model = os.environ.get("LEARN_MODEL", "gpt-4o-mini").strip()
    if base and key:
        return APIBrain(base, key, model, offline)
    return offline
