# tests/test_predict.py

import unittest
from gcp_mft_ai.predict import predict_transfer_time

class TestPredict(unittest.TestCase):
    def test_predict_transfer_time(self):
        """Test prediction fallback and result."""
        predicted_time = predict_transfer_time(file_size_mb=500)
        self.assertTrue(predicted_time > 0)

if __name__ == "__main__":
    unittest.main()
