import unittest

import epubgrep


class TestEPubGrep(unittest.TestCase):
    def test_epub_is_file(self):
        with self.assertRaises(AssertionError):
            epubgrep.grep_book("foo", "bar", 0)
