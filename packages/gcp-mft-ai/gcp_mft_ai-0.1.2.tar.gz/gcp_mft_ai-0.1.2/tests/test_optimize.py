# tests/test_optimize.py

import unittest
import pandas as pd
from gcp_mft_ai.optimize import find_best_transfer_window

class TestOptimize(unittest.TestCase):
    def test_find_best_window(self):
        """Test optimizing best transfer window from fake logs."""
        data = {
            "file_size_mb": [10, 20, 30, 40, 50],
            "transfer_time_sec": [5, 5, 4, 3, 2],
            "timestamp": [
                "2024-04-25T01:00:00",
                "2024-04-25T01:30:00",
                "2024-04-25T02:00:00",
                "2024-04-25T02:30:00",
                "2024-04-25T03:00:00"
            ]
        }
        df = pd.DataFrame(data)
        test_csv = "test_optimize_log.csv"
        df.to_csv(test_csv, index=False)

        best_window = find_best_transfer_window(test_csv)
        self.assertIn("best_hour", best_window)
        self.assertIn("avg_speed_mb_per_sec", best_window)

if __name__ == "__main__":
    unittest.main()
