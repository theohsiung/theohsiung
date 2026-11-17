import unittest
from datetime import timedelta

from helpers import NOW
from text import ago, truncate


class TextTest(unittest.TestCase):
    def test_truncate(self):
        self.assertEqual(truncate("short", 10), "short")
        self.assertEqual(truncate("a long title here", 8), "a long…")
        self.assertEqual(len(truncate("x" * 50, 20)), 20)

    def test_ago(self):
        cases = {0: "today", 3: "3d ago", 20: "2w ago", 90: "3mo ago", 800: "2y ago"}
        for days, label in cases.items():
            with self.subTest(days=days):
                self.assertEqual(ago(NOW - timedelta(days=days), NOW), label)


if __name__ == "__main__":
    unittest.main()
