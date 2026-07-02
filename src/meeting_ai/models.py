from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Evidence:
    quote: str
    timestamp: str
    speaker: str


@dataclass
class ActionItem:
    task: str
    owner: str = "Unassigned"
    deadline: str | None = None
    priority: str = "medium"
    confidence: float = 0.75
    evidence: Evidence | None = None


@dataclass
class Decision:
    text: str
    confidence: float = 0.8
    evidence: Evidence | None = None


@dataclass
class Question:
    text: str
    asked_by: str
    answered: bool = False
    evidence: Evidence | None = None


@dataclass
class Risk:
    text: str
    severity: str = "medium"
    evidence: Evidence | None = None


@dataclass
class MeetingIntelligence:
    meeting_id: str
    title: str
    goal: str
    summary: str
    decisions: list[Decision] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    questions: list[Question] = field(default_factory=list)
    risks: list[Risk] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    participation: dict[str, float] = field(default_factory=dict)
    model: str = "baseline-v1"
    prompt_version: str = "v1"
    latency_ms: float = 0
    estimated_cost_usd: float = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
