# -*- coding: utf-8 -*-
"""SQLite 持久化：会话、事件、掌握度、复习队列。仅存本机 data/learn.db。"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time

DAY = 86400
INTERVALS = (1, 3, 7, 16)  # 简化 SM-2：答对推进、答错退回 1 天


class Store:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.path = db_path
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._lock, self.conn:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    topic_id TEXT NOT NULL,
                    phase TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    topic_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    ts REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mastery (
                    topic_id TEXT PRIMARY KEY,
                    mastered INTEGER NOT NULL DEFAULT 0,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    reps INTEGER NOT NULL DEFAULT 0,
                    interval_days INTEGER NOT NULL DEFAULT 0,
                    due_at REAL NOT NULL DEFAULT 0,
                    wrong_steps TEXT NOT NULL DEFAULT '[]',
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    topic_id TEXT PRIMARY KEY,
                    due_at REAL NOT NULL,
                    interval_days INTEGER NOT NULL,
                    reps INTEGER NOT NULL DEFAULT 0,
                    last_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_reviews_due ON reviews(due_at);
                """
            )

    # ---------- 会话 ----------
    def log_event(self, session_id: str, topic_id: str, kind: str,
                  payload: dict, ts: float | None = None):
        ts = ts or time.time()
        with self._lock, self.conn:
            self.conn.execute(
                "INSERT INTO events(session_id,topic_id,kind,payload,ts) VALUES(?,?,?,?,?)",
                (session_id, topic_id, kind, json.dumps(payload, ensure_ascii=False), ts),
            )
            self.conn.execute(
                """INSERT INTO sessions(id,topic_id,phase,created_at,updated_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET updated_at=excluded.updated_at""",
                (session_id, topic_id, "active", ts, ts),
            )

    # ---------- 掌握度 ----------
    def get_mastery(self, topic_id: str) -> dict:
        with self._lock:
            row = self.conn.execute(
                "SELECT * FROM mastery WHERE topic_id=?", (topic_id,)
            ).fetchone()
        if row is None:
            return {"mastered": 0, "attempts": 0, "reps": 0,
                    "interval_days": 0, "due_at": 0, "wrong_steps": []}
        return dict(row) | {"wrong_steps": json.loads(row["wrong_steps"] or "[]")}

    def record_attempt(self, topic_id: str, correct: bool, wrong_step: int):
        """幂等语义：按 topic 累计一次尝试；错步去重记录。"""
        now = time.time()
        with self._lock, self.conn:
            row = self.conn.execute(
                "SELECT * FROM mastery WHERE topic_id=?", (topic_id,)
            ).fetchone()
            if row is None:
                self.conn.execute(
                    """INSERT INTO mastery(topic_id,mastered,attempts,reps,
                       interval_days,due_at,wrong_steps,updated_at)
                       VALUES(?,0,1,0,0,0,?,?)""",
                    (topic_id,
                     json.dumps([wrong_step] if not correct else []), now),
                )
                return
            steps = json.loads(row["wrong_steps"] or "[]")
            if not correct and wrong_step not in steps:
                steps.append(wrong_step)
            self.conn.execute(
                """UPDATE mastery SET attempts=attempts+1, wrong_steps=?, updated_at=?
                   WHERE topic_id=?""",
                (json.dumps(steps), now, topic_id),
            )

    def mark_mastered(self, topic_id: str, wrong_steps: list[int]):
        now = time.time()
        with self._lock, self.conn:
            row = self.conn.execute(
                "SELECT * FROM mastery WHERE topic_id=?", (topic_id,)
            ).fetchone()
            if row is None:
                self.conn.execute(
                    """INSERT INTO mastery(topic_id,mastered,attempts,reps,
                       interval_days,due_at,wrong_steps,updated_at)
                       VALUES(?,1,0,0,0,0,?,?)""",
                    (topic_id, json.dumps(wrong_steps), now),
                )
            else:
                self.conn.execute(
                    "UPDATE mastery SET mastered=1, wrong_steps=?, updated_at=? WHERE topic_id=?",
                    (json.dumps(sorted(set(wrong_steps))), now, topic_id),
                )

    # ---------- 间隔复习（简化 SM-2）----------
    def schedule_review(self, topic_id: str, correct: bool = True) -> float:
        now = time.time()
        with self._lock, self.conn:
            row = self.conn.execute(
                "SELECT * FROM reviews WHERE topic_id=?", (topic_id,)
            ).fetchone()
            reps = 0 if row is None else int(row["reps"])
            if not correct:
                reps = 0
                days = INTERVALS[0]
            else:
                reps += 1
                days = INTERVALS[min(reps - 1, len(INTERVALS) - 1)]
            due = now + days * DAY
            self.conn.execute(
                """INSERT INTO reviews(topic_id,due_at,interval_days,reps,last_at)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(topic_id) DO UPDATE SET
                     due_at=excluded.due_at, interval_days=excluded.interval_days,
                     reps=excluded.reps, last_at=excluded.last_at""",
                (topic_id, due, days, reps, now),
            )
            self.conn.execute(
                "UPDATE mastery SET interval_days=?, due_at=?, reps=? WHERE topic_id=?",
                (days, due, reps, topic_id),
            )
        return due

    def due_reviews(self, now: float | None = None) -> list[dict]:
        now = now or time.time()
        with self._lock:
            rows = self.conn.execute(
                "SELECT * FROM reviews WHERE due_at<=? ORDER BY due_at", (now,)
            ).fetchall()
        return [dict(r) for r in rows]

    def upcoming_reviews(self, now: float | None = None) -> list[dict]:
        now = now or time.time()
        with self._lock:
            rows = self.conn.execute(
                "SELECT * FROM reviews ORDER BY due_at LIMIT 20"
            ).fetchall()
        return [dict(r) | {"days_left": max(0, round((r["due_at"] - now) / DAY, 1))}
                for r in rows]

    def progress(self) -> dict:
        with self._lock:
            rows = self.conn.execute("SELECT * FROM mastery").fetchall()
            ev = self.conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
        mastered = sum(1 for r in rows if r["mastered"])
        attempts = sum(int(r["attempts"]) for r in rows)
        return {
            "topics_started": len(rows),
            "topics_mastered": mastered,
            "total_attempts": attempts,
            "total_events": ev,
            "wrong_steps_total": sum(len(json.loads(r["wrong_steps"] or "[]")) for r in rows),
        }

    def reset(self):
        with self._lock, self.conn:
            for t in ("sessions", "events", "mastery", "reviews"):
                self.conn.execute(f"DELETE FROM {t}")
