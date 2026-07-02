from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from meeting_ai.evaluate import run_benchmark
from meeting_ai.extractor import extract_meeting


def main() -> None:
    dataset = json.loads((ROOT / "datasets" / "benchmark.json").read_text())
    outputs = [extract_meeting(case["id"], case["title"], case["transcript"]).to_dict() for case in dataset]
    benchmark = run_benchmark(ROOT / "datasets" / "benchmark.json")
    (ROOT / "benchmark" / "results.json").write_text(json.dumps(benchmark, indent=2))
    (ROOT / "datasets" / "processed.json").write_text(json.dumps(outputs, indent=2))
    print(f"Processed {len(outputs)} meetings | action F1={benchmark['metrics']['action_f1']:.3f} | decision F1={benchmark['metrics']['decision_f1']:.3f}")


if __name__ == "__main__":
    main()
