import json
import unittest

from fastapi.testclient import TestClient

from app.main import app, WEBHOOK_PATH


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_info(self):
        response = self.client.get(f"{WEBHOOK_PATH}/info")
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIsInstance(response_data, dict)

    def test_clear_db(self):
        response = self.client.get(f"{WEBHOOK_PATH}/clear")
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIsInstance(response_data, str)
        self.assertIn("All values removed", response_data)

    def test_add_remind(self):
        remind = {
            "user_id": 1,
            "name": "Test",
            "date": "2022-01-01 00:00:00",
            "text": "Test Reminder"
        }
        response = self.client.post(f"{WEBHOOK_PATH}/post", json=remind)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content)
        self.assertIsInstance(response_data, list)
        self.assertIn(remind["user_id"], response_data)
        self.assertEqual(response_data[1], remind["user_id"])


if __name__ == '__main__':
    unittest.main()
