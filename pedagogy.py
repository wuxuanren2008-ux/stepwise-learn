# -*- coding: utf-8 -*-
"""四阶段教学法状态机（复刻 Sia：提示 → 演练 → 检查站 → 测验）。

对外接口：
    Session(topic_id, brain, store)  ->  session
    session.advance(action, payload) ->  frame(dict)
    frame 字段固定：phase / title / cue / board(list[str]) / narration /
                    options / feedback / progress / step_index / total_steps /
                    mode / next_actions / mastery / due_review
action 取值：start | hint | reveal | answer | quiz_answer | restart
"""
from __future__ import annotations

import time
import uuid

from curriculum import get_topic

PHASES = ("hint", "walkthrough", "checkpoint", "quiz", "mastered")
INTERVALS = (1, 3, 7, 16)  # 简化 SM-2，单位：天


class Session:
    def __init__(self, topic_id: str, brain, store, session_id: str | None = None):
        topic = get_topic(topic_id)
        if topic is None:
            raise ValueError(f"unknown topic: {topic_id}")
        self.topic = topic
        self.topic_id = topic_id
        self.brain = brain
        self.store = store
        self.id = session_id or uuid.uuid4().hex[:12]
        self.phase = "hint"
        self.step_index = 0          # 已揭示到第几步（0 表示还没揭示）
        self.quiz_index = 0
        self.wrong_steps: list[int] = []
        self.attempts = 0
        self.created_at = time.time()
        self._last_feedback = ""

    # ---------- 内部工具 ----------
    def _board(self) -> list[str]:
        return [s["board"] for s in self.topic["steps"][: self.step_index]]

    def _mastery(self) -> dict:
        m = self.store.get_mastery(self.topic_id)
        return {
            "mastered": m.get("mastered", 0),
            "attempts": m.get("attempts", 0),
            "reps": m.get("reps", 0),
            "interval_days": m.get("interval_days", 0),
            "due_at": m.get("due_at", 0),
            "wrong_steps": self.wrong_steps,
        }

    def _frame(self, narration: str, *, options=None, feedback: str = "",
               next_actions: list[str] | None = None) -> dict:
        total = len(self.topic["steps"])
        if self.phase == "hint":
            progress = 0.0
        elif self.phase == "walkthrough":
            progress = 0.1 + 0.5 * (self.step_index / total)
        elif self.phase == "checkpoint":
            progress = 0.65
        elif self.phase == "quiz":
            progress = 0.7 + 0.25 * (self.quiz_index / max(1, len(self.topic["quiz"])))
        else:
            progress = 1.0
        return {
            "session_id": self.id,
            "topic_id": self.topic_id,
            "course_title": self.topic["course_title"],
            "title": self.topic["title"],
            "goal": self.topic["goal"],
            "cue": self.topic["cue"],
            "phase": self.phase,
            "board": self._board(),
            "step_index": self.step_index,
            "total_steps": total,
            "narration": narration,
            "options": options,
            "feedback": feedback,
            "progress": round(progress, 3),
            "mode": self.brain.mode,
            "next_actions": next_actions or [],
            "mastery": self._mastery(),
            "misconception": (
                self.topic["steps"][self.step_index - 1]["misconception"]
                if self.step_index > 0 and self.step_index <= total else ""
            ),
        }

    # ---------- 状态机 ----------
    def advance(self, action: str, payload: dict | None = None) -> dict:
        payload = payload or {}
        now = time.time()
        self.store.log_event(self.id, self.topic_id, action, payload, now)

        if action == "restart":
            self.__init__(self.topic_id, self.brain, self.store, self.id)
            return self.advance("start")

        if action == "start":
            self.phase = "hint"
            self.step_index = 0
            text = self.brain.narrate(
                "hint", self.topic, {"cue": self.topic["cue"], "step_index": 0}
            )
            return self._frame(
                text,
                next_actions=[
                    {"action": "hint", "label": "再给一点提示"},
                    {"action": "reveal", "label": "我自己先试，看下一步"},
                ],
            )

        if action == "hint":
            # 硬规则：提示阶段绝不下发任何 step 的 board 或 say
            text = self.brain.narrate(
                "hint_again", self.topic,
                {"cue": self.topic["cue"], "attempts": self.attempts},
            )
            self.attempts += 1
            return self._frame(
                text,
                next_actions=[
                    {"action": "hint", "label": "再换个角度提示"},
                    {"action": "reveal", "label": "看第一步"},
                ],
            )

        if action == "reveal":
            total = len(self.topic["steps"])
            if self.phase in ("hint", "walkthrough"):
                if self.step_index >= total:
                    return self._to_checkpoint()
                step = self.topic["steps"][self.step_index]
                self.step_index += 1
                self.phase = "walkthrough"
                text = self.brain.narrate(
                    "reveal", self.topic,
                    {"step_index": self.step_index, "board": step["board"],
                     "say": step["say"], "misconception": step["misconception"]},
                )
                actions = [
                    {"action": "reveal", "label": "继续下一步" if self.step_index < total else "进入检查站"},
                    {"action": "hint", "label": "这一步没懂，换个说法"},
                ]
                return self._frame(text, next_actions=actions)
            return self._frame("当前阶段不支持该操作。", next_actions=[])

        if action == "answer":
            if self.phase != "checkpoint":
                return self._frame("现在不需要作答，继续看步骤即可。",
                                   next_actions=[{"action": "reveal", "label": "继续"}])
            cp = self.topic["checkpoint"]
            choice = int(payload.get("index", -1))
            self.attempts += 1
            if choice == cp["answer"]:
                self.store.record_attempt(self.topic_id, True, 0)
                self.phase = "quiz"
                self.quiz_index = 0
                text = self.brain.narrate("checkpoint_ok", self.topic, {"why": cp["why"]})
                return self._frame(
                    text, feedback="答对了 ✓",
                    options=self.topic["quiz"][0]["options"],
                    next_actions=[{"action": "quiz_answer", "label": "提交答案"}],
                )
            # 答错：回退到对应错步并标记
            ws = int(cp.get("wrong_step", 0))
            self.wrong_steps.append(ws)
            self.store.record_attempt(self.topic_id, False, ws)
            self.step_index = min(ws + 1, len(self.topic["steps"]))
            step = self.topic["steps"][ws]
            text = self.brain.narrate(
                "checkpoint_wrong", self.topic,
                {"why": cp["why"], "misconception": step["misconception"],
                 "board": step["board"], "say": step["say"]},
            )
            return self._frame(
                text, feedback="这一步容易卡住，我们回到它",
                options=cp["options"],
                next_actions=[
                    {"action": "answer", "label": "重新作答"},
                    {"action": "reveal", "label": "重看后面的步骤"},
                ],
            )

        if action == "quiz_answer":
            if self.phase != "quiz":
                return self._frame("现在不在测验阶段。", next_actions=[])
            q = self.topic["quiz"][self.quiz_index]
            choice = int(payload.get("index", -1))
            self.attempts += 1
            if choice == q["answer"]:
                self.store.record_attempt(self.topic_id, True, 0)
                self.quiz_index += 1
                if self.quiz_index >= len(self.topic["quiz"]):
                    return self._finish()
                nxt = self.topic["quiz"][self.quiz_index]
                text = self.brain.narrate("quiz_ok", self.topic, {"why": q["why"]})
                return self._frame(
                    text, feedback="答对了 ✓", options=nxt["options"],
                    next_actions=[{"action": "quiz_answer", "label": "提交答案"}],
                )
            ws = max(0, min(self.step_index - 1, len(self.topic["steps"]) - 1))
            self.wrong_steps.append(ws)
            self.store.record_attempt(self.topic_id, False, ws)
            text = self.brain.narrate("quiz_wrong", self.topic, {"why": q["why"]})
            return self._frame(
                text, feedback="再想一下", options=q["options"],
                next_actions=[{"action": "quiz_answer", "label": "重新作答"}],
            )

        return self._frame("未知操作。", next_actions=[])

    def _to_checkpoint(self) -> dict:
        self.phase = "checkpoint"
        cp = self.topic["checkpoint"]
        text = self.brain.narrate(
            "checkpoint", self.topic, {"question": cp["question"]}
        )
        return self._frame(
            text, options=cp["options"],
            next_actions=[{"action": "answer", "label": "提交答案"}],
        )

    def _finish(self) -> dict:
        self.phase = "mastered"
        self.store.mark_mastered(self.topic_id, self.wrong_steps)
        due = self.store.schedule_review(self.topic_id, correct=True)
        text = self.brain.narrate("mastered", self.topic, {"due": due})
        return self._frame(
            text, feedback="这个知识点已经掌握，我们安排了之后的复习",
            next_actions=[
                {"action": "restart", "label": "再走一遍"},
                {"action": "start", "label": "回到开头"},
            ],
        )
