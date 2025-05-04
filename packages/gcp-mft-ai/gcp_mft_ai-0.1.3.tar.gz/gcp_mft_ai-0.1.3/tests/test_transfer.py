# tests/test_transfer.py

import unittest
from gcp_mft_ai.transfer import TransferManager

class TestTransfer(unittest.TestCase):
    def test_transfer_manager_gcs_upload_download(self):
        """Test that GCS transfer methods exist and can be initialized."""
        # We won't actually upload/download because GCP credentials are needed
        manager = TransferManager(bucket_name="dummy-bucket")
        self.assertIsNotNone(manager.client)
        self.assertEqual(manager.bucket.name, "dummy-bucket")

if __name__ == "__main__":
    unittest.main()
