import unittest
from pathlib import Path

import pandas as pd

from src.nlp.report_generator import generate_report
from src.utils.common import DISCLAIMER


class TestReportGeneration(unittest.TestCase):
    def test_report_file_created(self):
        tmp = Path("test_outputs/report_generation")
        tmp.mkdir(parents=True, exist_ok=True)
        metrics = tmp / "metrics.csv"
        out = tmp / "report.md"
        pd.DataFrame([{"model": "demo", "accuracy": 0.8, "f1_score": 0.75, "mae": None, "rmse": None}]).to_csv(metrics, index=False)
        text = generate_report(metrics, out, dataset="synthetic")
        self.assertTrue(out.exists())
        self.assertIn(DISCLAIMER, text)


if __name__ == "__main__":
    unittest.main()
