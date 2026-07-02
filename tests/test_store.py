import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from meeting_ai.store import MeetingStore


class StoreTests(unittest.TestCase):
    def test_save_search_and_feedback(self):
        with tempfile.TemporaryDirectory() as directory:
            store = MeetingStore(Path(directory) / "test.db")
            item = {"meeting_id": "m1", "title": "Auth", "topics": ["authentication"]}
            store.save("m1", "Auth", "transcript", item)
            self.assertEqual(store.get("m1"), item)
            self.assertEqual(store.search("authentication")[0]["meeting_id"], "m1")
            store.feedback("m1", 1, None)


if __name__ == "__main__":
    unittest.main()
