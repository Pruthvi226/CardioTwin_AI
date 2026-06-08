import unittest

from fastapi.testclient import TestClient

from src.api.main import app
from src.utils.common import DISCLAIMER


class TestAPI(unittest.TestCase):
    def test_health_and_sample_response(self):
        client = TestClient(app)
        self.assertEqual(client.get("/health").status_code, 200)
        sample = client.get("/sample-response").json()
        self.assertEqual(sample["disclaimer"], DISCLAIMER)


if __name__ == "__main__":
    unittest.main()

