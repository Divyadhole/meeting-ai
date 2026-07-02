import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from meeting_ai.extractor import extract_meeting, parse_transcript


TRANSCRIPT = """[00:00] Divya: We need to pick a launch date.
[00:15] Kai: We decided to launch on September 8.
[00:30] Divya: Kai will write the rollout plan by Friday.
[00:45] Kai: Are legal terms approved?
[01:00] Divya: Risk: the review queue is growing."""


class ExtractorTests(unittest.TestCase):
    def test_parse_speakers_and_timestamps(self):
        turns = parse_transcript(TRANSCRIPT)
        self.assertEqual(turns[1]["speaker"], "Kai")
        self.assertEqual(turns[1]["timestamp"], "00:15")

    def test_extracts_grounded_intelligence(self):
        result = extract_meeting("m1", "Launch", TRANSCRIPT)
        self.assertEqual(result.decisions[0].text, "launch on September 8")
        self.assertEqual(result.action_items[0].owner, "Kai")
        self.assertEqual(result.action_items[0].deadline, "Friday")
        self.assertEqual(len(result.questions), 1)
        self.assertEqual(result.risks[0].severity, "medium")
        self.assertIn(result.decisions[0].evidence.quote, TRANSCRIPT)


if __name__ == "__main__":
    unittest.main()
