import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        os.environ["MEETING_AI_DB"] = str(Path(cls.temp.name) / "api.db")
        from fastapi.testclient import TestClient
        from meeting_ai.api import app
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_health_and_ingestion(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.post("/api/meetings", json={
            "title": "Launch review",
            "transcript": "[00:00] Divya: We decided to launch Friday.\n[00:15] Sam: Divya will publish the plan by Thursday."
        })
        self.assertEqual(response.status_code, 200)
        meeting = response.json()
        self.assertEqual(meeting["decisions"][0]["text"], "launch Friday")
        feedback = self.client.post(f"/api/meetings/{meeting['meeting_id']}/feedback", json={"rating": 1})
        self.assertEqual(feedback.status_code, 204)
        self.assertEqual(feedback.content, b"")


if __name__ == "__main__":
    unittest.main()
