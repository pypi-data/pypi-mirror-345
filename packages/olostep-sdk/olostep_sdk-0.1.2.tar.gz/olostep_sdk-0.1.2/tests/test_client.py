import unittest

from olostep_sdk.client import OlostepClient


class TestOlostepClient(unittest.TestCase):
    def test_init_sets_token_and_url(self):
        client = OlostepClient(api_token="fake-token")
        self.assertEqual(client.api_token, "fake-token")
        self.assertEqual(client.base_url, "https://api.olostep.com/v1")
