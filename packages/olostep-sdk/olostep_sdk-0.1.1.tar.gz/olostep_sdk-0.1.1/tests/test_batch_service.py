import unittest
from unittest.mock import MagicMock

from olostep_sdk.client import OlostepClient
from olostep_sdk.services.batch import BatchService


class TestBatchService(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=OlostepClient)
        self.batch_service = BatchService(client=self.mock_client)

    def test_start_batch(self):
        self.mock_client._request.return_value = {"id": "batch123"}
        batch_id = self.batch_service.start_batch(
            items=[{"url": "https://example.com"}]
        )
        self.assertEqual(batch_id, "batch123")

    def test_get_status(self):
        self.mock_client._request.return_value = {"status": "completed"}
        status = self.batch_service.get_status("batch123")
        self.assertEqual(status, "completed")

    def test_wait_until_complete(self):
        self.mock_client._request.side_effect = [
            {"status": "in_progress"},
            {"status": "completed"},
        ]
        self.batch_service.wait_until_complete("batch123", interval=0)

    def test_get_items(self):
        self.mock_client._request.return_value = {
            "items": [{"url": "https://example.com"}]
        }
        items = self.batch_service.get_items("batch123")
        self.assertEqual(len(items), 1)

    def test_retrieve_content(self):
        self.mock_client._request.return_value = {"json": "ok"}
        result = self.batch_service.retrieve_content("retrieve123")
        self.assertEqual(result["json"], "ok")
