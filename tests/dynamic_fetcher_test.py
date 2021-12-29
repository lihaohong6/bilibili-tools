import unittest

from dynamic_fetcher import make_multiline


class TestDynamicFetcher(unittest.TestCase):
    def test_make_multiline_with_single_paragraph(self):
        text = "123456789"
        self.assertEqual(make_multiline(text, 100), text)
        self.assertEqual(make_multiline(text, 8), "12345678\n9")
        self.assertEqual(make_multiline(text, 4), "1234\n5678\n9")

    def test_make_multiline_with_multiple_paragraphs(self):
        text = "12345\n67890"
        self.assertEqual(make_multiline(text, 3), "123\n45\n\n678\n90")


if __name__ == '__main__':
    unittest.main()
