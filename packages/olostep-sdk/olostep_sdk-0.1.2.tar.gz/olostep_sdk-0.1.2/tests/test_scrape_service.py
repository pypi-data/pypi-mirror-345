import unittest
from unittest.mock import MagicMock

from olostep_sdk.client import OlostepClient
from olostep_sdk.enums import Format, OlostepParser
from olostep_sdk.services.scrape import ScrapeService


class TestScrapeService(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=OlostepClient)
        self.scrape_service = ScrapeService(client=self.mock_client)

    def test_scrape_default_format(self):
        self.mock_client._request.return_value = {"id": "123"}
        response = self.scrape_service.scrape("https://example.com")
        self.assertEqual(response, {"id": "123"})

    def test_scrape_with_parser_and_format(self):
        self.mock_client._request.return_value = {"id": "123"}
        response = self.scrape_service.scrape(
            "https://example.com",
            formats=[Format.HTML, Format.MARKDOWN],
            parser=OlostepParser.GOOGLE_SEARCH,
        )
        self.mock_client._request.assert_called_once()
