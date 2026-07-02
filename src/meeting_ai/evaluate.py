from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from .extractor import extract_meeting


def _f1(predicted: list[str], expected: list[str]) -> tuple[float, float, float]:
    pred, gold = set(predicted), set(expected)
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else (1.0 if not gold else 0.0)
    recall = tp / len(gold) if gold else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def run_benchmark(dataset_path: str | Path) -> dict:
    cases = json.loads(Path(dataset_path).read_text())
    rows = []
    for case in cases:
        started = time.perf_counter()
        result = extract_meeting(case["id"], case["title"], case["transcript"])
        expected = case["expected"]
        action = _f1([x.task.lower() for x in result.action_items], [x.lower() for x in expected["actions"]])
        decision = _f1([x.text.lower() for x in result.decisions], [x.lower() for x in expected["decisions"]])
        claims = [*result.action_items, *result.decisions, *result.risks, *result.questions]
        hallucination = 1 - sum(bool(x.evidence and x.evidence.quote in case["transcript"]) for x in claims) / max(len(claims), 1)
        rows.append({"id": case["id"], "action_precision": action[0], "action_recall": action[1], "action_f1": action[2], "decision_precision": decision[0], "decision_recall": decision[1], "decision_f1": decision[2], "hallucination_rate": hallucination, "json_validity": 1.0, "latency_ms": (time.perf_counter() - started) * 1000, "cost_usd": 0.0})
    metric_names = [k for k in rows[0] if k != "id"]
    return {"model": "baseline-v1", "prompt_version": "v1", "cases": len(rows), "metrics": {key: round(statistics.mean(row[key] for row in rows), 4) for key in metric_names}, "results": rows}
