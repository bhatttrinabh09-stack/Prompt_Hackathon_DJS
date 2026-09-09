import unittest
from fastapi.testclient import TestClient
from main import app
from ranking import rank_topics, infer_prerequisites
from summarizer import condense_topic
from script_gen import generate_short_script, render_video_stub


class TestMLService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_ranking(self):
        ranked = rank_topics("os-sem3-aiml")
        self.assertEqual(len(ranked), 10)
        self.assertTrue(any(r["must_ask"] for r in ranked))
        self.assertGreater(ranked[0]["importance_score"], ranked[-1]["importance_score"])

    def test_prerequisites(self):
        prereqs = infer_prerequisites("os-t06")
        self.assertGreaterEqual(len(prereqs), 1)

    def test_condense(self):
        result = condense_topic("os-t06", target_ratio=0.25)
        self.assertIn("bullets", result)
        self.assertGreaterEqual(len(result["bullets"]), 1)
        self.assertLess(result["actual_ratio"], 0.7)

    def test_script_gen(self):
        script = generate_short_script("os-t03")
        self.assertIn("hook", script)
        self.assertIn("beat_1", script)
        self.assertIn("exam_trick", script)
        self.assertGreaterEqual(script["est_duration_seconds"], 20)

        video = render_video_stub(script, "os-t03")
        self.assertEqual(video["status"], "rendered")
        self.assertTrue(video["asset_url"].startswith("http"))

    def test_api_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertEqual(data["topics_loaded"], 10)

    def test_api_rank_topics(self):
        res = self.client.post("/rank-topics", json={"subject_id": "os-sem3-aiml"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_topics"], 10)

    def test_api_condense(self):
        res = self.client.post("/condense", json={"topic_id": "os-t01", "target_ratio": 0.25})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("bullets", data)

    def test_api_generate_short(self):
        res = self.client.post("/generate-short", json={"topic_id": "os-t02"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("script", data)
        self.assertIn("video", data)


if __name__ == "__main__":
    unittest.main()
