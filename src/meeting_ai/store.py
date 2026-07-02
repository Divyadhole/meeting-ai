from __future__ import annotations

import json
import sqlite3
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
