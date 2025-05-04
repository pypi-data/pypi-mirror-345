# tests/test_anomaly.py

import unittest
import pandas as pd
from gcp_mft_ai.anomaly import detect_transfer_anomalies

class TestAnomaly(unittest.TestCase):
    def test_detect_anomalies_basic(self):
        """Test anomaly detection on synthetic data."""
        data = {
            "file_size_mb": [10, 20, 30, 4000, 50, 60],
            "transfer_time_sec": [1, 2, 3, 500, 5, 6]
        }
        df = pd.DataFrame(data)
        test_csv = "test_transfer_log.csv"
        df.to_csv(test_csv, index=False)

        anomalies = detect_transfer_anomalies(test_csv)
        self.assertGreaterEqual(len(anomalies), 1)

if __name__ == "__main__":
    unittest.main()
