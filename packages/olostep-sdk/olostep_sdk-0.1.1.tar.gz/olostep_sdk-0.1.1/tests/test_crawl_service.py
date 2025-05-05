import unittest
from unittest.mock import MagicMock

from olostep_sdk.client import OlostepClient
from olostep_sdk.services.crawl import CrawlService


class TestCrawlService(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=OlostepClient)
        self.crawl_service = CrawlService(client=self.mock_client)

    def test_start_crawl(self):
        self.mock_client._request.return_value = {"id": "crawl123"}
        result = self.crawl_service.start_crawl("https://example.com")
        self.assertEqual(result["id"], "crawl123")

    def test_get_crawl_status(self):
        self.mock_client._request.return_value = {"status": "completed"}
        status = self.crawl_service.get_crawl_status("crawl123")
        self.assertEqual(status, "completed")

    def test_get_pages(self):
        self.mock_client._request.return_value = {"pages": []}
        result = self.crawl_service.get_pages("crawl123")
        self.assertEqual(result, {"pages": []})

    def test_retrieve_content(self):
        self.mock_client._request.return_value = {"json": "data"}
        result = self.crawl_service.retrieve_content("retrieve123")
        self.assertEqual(result, {"json": "data"})
