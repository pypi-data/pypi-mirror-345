import unittest

from olostep_sdk.enums import Format, OlostepParser


class TestEnums(unittest.TestCase):
    def test_parser_enum(self):
        self.assertEqual(str(OlostepParser.GOOGLE_SEARCH), "@olostep/google-search")

    def test_format_enum(self):
        self.assertEqual(str(Format.MARKDOWN), "markdown")
