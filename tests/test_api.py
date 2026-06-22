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
        self.assertIn("similar_windows", sample)

    def test_model_info_reports_vector_database(self):
        client = TestClient(app)
        info = client.get("/model-info").json()
        self.assertIn("vector_database", info)
        self.assertEqual(info["vector_database"]["backend"], "sklearn_nearest_neighbors")


if __name__ == "__main__":
    unittest.main()
