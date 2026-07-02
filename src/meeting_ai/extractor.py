from __future__ import annotations

import re
import time
from collections import Counter

from .models import ActionItem, Decision, Evidence, MeetingIntelligence, Question, Risk

LINE = re.compile(r"(?:\[(?P<time>\d\d:\d\d)\]\s*)?(?P<speaker>[A-Za-z][\w .'-]{0,30}):\s*(?P<text>.+)")
DECISION = re.compile(r"\b(?:we (?:decided|will|chose|agreed)|decision(?: is)?|let'?s)\b[:,]?\s*(?:to\s+)?(.+)", re.I)
ACTION = re.compile(r"\b(?:(?P<owner>[A-Z][a-z]+),? (?:will|can you|please)|I(?:'ll| will)|action item(?: for [A-Z][a-z]+)?(?: is)?)[,:]?\s*(?P<task>.+)", re.I)
RISK = re.compile(r"\b(?:risk|blocked|blocker|concern|might slip|at risk)\b[:,]?\s*(.*)", re.I)
DEADLINE = re.compile(r"\b(by|before|due)\s+((?:next\s+)?(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)|today|tomorrow|EOD|\w+ \d{1,2})\b", re.I)
STOP = {"the", "and", "that", "this", "with", "from", "have", "will", "should", "about", "into", "your", "we're", "they", "then"}


def parse_transcript(transcript: str) -> list[dict[str, str]]:
    turns = []
    for index, raw in enumerate(transcript.splitlines()):
        raw = raw.strip()
        if not raw:
            continue
        match = LINE.match(raw)
        if match:
            turns.append({"timestamp": match.group("time") or f"00:{index * 15:02d}", "speaker": match.group("speaker"), "text": match.group("text")})
        else:
            turns.append({"timestamp": f"00:{index * 15:02d}", "speaker": "Unknown", "text": raw})
    return turns


def _evidence(turn: dict[str, str]) -> Evidence:
    return Evidence(quote=turn["text"], timestamp=turn["timestamp"], speaker=turn["speaker"])


def _topics(turns: list[dict[str, str]]) -> list[str]:
    words = re.findall(r"[a-z][a-z0-9-]{3,}", " ".join(t["text"].lower() for t in turns))
    return [word.title() for word, _ in Counter(w for w in words if w not in STOP).most_common(6)]


def extract_meeting(meeting_id: str, title: str, transcript: str, prompt_version: str = "v1") -> MeetingIntelligence:
    started = time.perf_counter()
    turns = parse_transcript(transcript)
    decisions, actions, questions, risks = [], [], [], []
    counts = Counter(t["speaker"] for t in turns)
    for turn in turns:
        text = turn["text"].strip()
        if match := DECISION.search(text):
            decisions.append(Decision(match.group(1).rstrip("."), 0.88, _evidence(turn)))
        if match := ACTION.search(text):
            owner = match.group("owner") or turn["speaker"]
            task = match.group("task").rstrip(".")
            due = DEADLINE.search(task)
            deadline = due.group(2) if due else None
            actions.append(ActionItem(task, owner, deadline, "high" if "urgent" in text.lower() else "medium", 0.84, _evidence(turn)))
        if "?" in text:
            questions.append(Question(text, turn["speaker"], False, _evidence(turn)))
        if match := RISK.search(text):
            risk_text = match.group(1).strip(" :,.—-") or text
            severity = "high" if any(w in text.lower() for w in ("critical", "security", "urgent", "blocked")) else "medium"
            risks.append(Risk(risk_text, severity, _evidence(turn)))
    total = max(sum(counts.values()), 1)
    participation = {speaker: round(100 * count / total, 1) for speaker, count in counts.items()}
    first = turns[0]["text"] if turns else "No transcript supplied."
    summary_bits = []
    if decisions:
        summary_bits.append(f"The team made {len(decisions)} decision{'s' if len(decisions) != 1 else ''}.")
    if actions:
        summary_bits.append(f"They assigned {len(actions)} action item{'s' if len(actions) != 1 else ''}.")
    if risks:
        summary_bits.append(f"{len(risks)} risk{'s were' if len(risks) != 1 else ' was'} flagged.")
    return MeetingIntelligence(
        meeting_id=meeting_id, title=title, goal=first.rstrip("."),
        summary=" ".join(summary_bits) or "Discussion captured; no explicit commitments were detected.",
        decisions=decisions, action_items=actions, questions=questions, risks=risks,
        topics=_topics(turns), participation=participation, prompt_version=prompt_version,
        latency_ms=round((time.perf_counter() - started) * 1000, 2),
    )
