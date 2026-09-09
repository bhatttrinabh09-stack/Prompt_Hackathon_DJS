import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine, SessionLocal
from app.seed import seed_database


class TestBackendService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed_database(db)
        cls.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["topics"], 10)

    def test_auth_flow(self):
        email = "testuser_suite@adaptlearn.dev"
        # Signup
        res_signup = self.client.post("/auth/signup", json={
            "name": "Suite Tester",
            "email": email,
            "password": "pass123tester",
            "branch": "AIML",
            "semester": 3,
        })
        # If already signed up or newly created
        if res_signup.status_code == 200:
            token = res_signup.json()["access_token"]
        else:
            res_login = self.client.post("/auth/login", json={
                "email": email,
                "password": "pass123tester",
            })
            self.assertEqual(res_login.status_code, 200)
            token = res_login.json()["access_token"]

        self.assertTrue(bool(token))

        # Test /user/me
        res_me = self.client.get("/user/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], email)

    def test_catalog_subjects_and_topics(self):
        res_sub = self.client.get("/subjects?branch=AIML&semester=3")
        self.assertEqual(res_sub.status_code, 200)
        subs = res_sub.json()
        self.assertGreaterEqual(len(subs), 1)
        sub_id = subs[0]["id"]

        res_topics = self.client.get(f"/subjects/{sub_id}/topics")
        self.assertEqual(res_topics.status_code, 200)
        topics = res_topics.json()
        self.assertEqual(len(topics), 10)

    def test_panic_session_lifecycle(self):
        # Create 2-hour panic session (< 72h -> high urgency)
        res = self.client.post("/panic-session", json={
            "examIn": 2,
            "unit": "hours",
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["urgencyLevel"], "high")

        # Check active session
        res_active = self.client.get("/panic-session/active")
        self.assertEqual(res_active.status_code, 200)
        self.assertTrue(res_active.json()["active"])
        self.assertEqual(res_active.json()["session"]["urgencyLevel"], "high")

    def test_cards_and_content_filtering(self):
        # Test cards
        res_cards = self.client.get("/topics/os-t01/cards")
        self.assertEqual(res_cards.status_code, 200)
        cards = res_cards.json()
        self.assertEqual(len(cards), 3)  # fast, dense, short_video

        # Test content with low urgency header
        res_content_low = self.client.get(
            "/topics/os-t01/content",
            headers={"X-Urgency-Level": "low"}
        )
        self.assertEqual(res_content_low.status_code, 200)
        self.assertEqual(res_content_low.json()["urgency_applied"], "low")

        # Test content with medium urgency (condenses notes)
        res_content_med = self.client.get(
            "/topics/os-t01/content?mode=dense",
            headers={"X-Urgency-Level": "medium"}
        )
        self.assertEqual(res_content_med.status_code, 200)
        self.assertEqual(res_content_med.json()["urgency_applied"], "medium")

    def test_swipe_and_progress(self):
        # Record swipe
        res_swipe = self.client.post("/swipe-event", json={
            "topicId": "os-t01",
            "cardId": "os-t01-dense",
            "cardType": "dense",
            "direction": "right",
        })
        self.assertEqual(res_swipe.status_code, 200)
        self.assertEqual(res_swipe.json()["status"], "recorded")

        # Mark complete
        res_complete = self.client.post("/progress/complete", json={
            "topicId": "os-t01",
            "mode": "dense",
        })
        self.assertEqual(res_complete.status_code, 200)

        # Check progress
        res_prog = self.client.get("/progress?subjectId=os-sem3-aiml")
        self.assertEqual(res_prog.status_code, 200)
        prog = res_prog.json()
        self.assertGreaterEqual(prog["overallPercentComplete"], 10.0)


if __name__ == "__main__":
    unittest.main()
