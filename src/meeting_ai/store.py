from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path


class MeetingStore:
    def __init__(self, path: str | Path = "meeting_ai.db") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS meetings (id TEXT PRIMARY KEY, title TEXT NOT NULL, transcript TEXT NOT NULL, intelligence TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, meeting_id TEXT NOT NULL, rating INTEGER NOT NULL, correction TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)

    def save(self, meeting_id: str, title: str, transcript: str, intelligence: dict) -> None:
        self.connection.execute("INSERT OR REPLACE INTO meetings(id,title,transcript,intelligence) VALUES(?,?,?,?)", (meeting_id, title, transcript, json.dumps(intelligence)))
        self.connection.commit()

    def all(self) -> list[dict]:
        rows = self.connection.execute("SELECT intelligence FROM meetings ORDER BY created_at DESC").fetchall()
        return [json.loads(row[0]) for row in rows]

    def get(self, meeting_id: str) -> dict | None:
        row = self.connection.execute("SELECT intelligence FROM meetings WHERE id=?", (meeting_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def search(self, query: str) -> list[dict]:
        tokens = set(query.lower().split())
        scored = []
        for meeting in self.all():
            haystack = json.dumps(meeting).lower()
            score = sum(haystack.count(token) for token in tokens)
            if score:
                scored.append((score, meeting))
        return [meeting for _, meeting in sorted(scored, key=lambda x: x[0], reverse=True)]

    def feedback(self, meeting_id: str, rating: int, correction: str | None) -> None:
        self.connection.execute("INSERT INTO feedback(meeting_id,rating,correction) VALUES(?,?,?)", (meeting_id, rating, correction))
        self.connection.commit()

    def analytics(self) -> dict:
        meetings = self.all()
        topics: Counter[str] = Counter()
        speakers: Counter[str] = Counter()
        for meeting in meetings:
            topics.update(meeting.get("topics", []))
            speakers.update(meeting.get("participation", {}))
        feedback_rows = self.connection.execute(
            "SELECT rating, COUNT(*) AS count FROM feedback GROUP BY rating"
        ).fetchall()
        return {
            "meetings": len(meetings),
            "decisions": sum(len(item.get("decisions", [])) for item in meetings),
            "action_items": sum(len(item.get("action_items", [])) for item in meetings),
            "open_questions": sum(len(item.get("questions", [])) for item in meetings),
            "risks": sum(len(item.get("risks", [])) for item in meetings),
            "top_topics": [{"name": name, "count": count} for name, count in topics.most_common(8)],
            "active_speakers": [{"name": name, "share": round(share, 1)} for name, share in speakers.most_common(8)],
            "feedback": {str(row["rating"]): row["count"] for row in feedback_rows},
        }

    def feedback_examples(self) -> list[dict]:
        rows = self.connection.execute(
            """SELECT f.meeting_id, f.rating, f.correction, f.created_at, m.title, m.transcript, m.intelligence
               FROM feedback f JOIN meetings m ON m.id=f.meeting_id ORDER BY f.created_at DESC"""
        ).fetchall()
        return [{
            "meeting_id": row["meeting_id"], "title": row["title"], "rating": row["rating"],
            "correction": row["correction"], "created_at": row["created_at"],
            "transcript": row["transcript"], "original_output": json.loads(row["intelligence"]),
        } for row in rows]
