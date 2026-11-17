import unittest

from text import truncate


class TextTest(unittest.TestCase):
    def test_truncate(self):
        self.assertEqual(truncate("short", 10), "short")
        self.assertEqual(truncate("a long title here", 8), "a long…")
        self.assertEqual(len(truncate("x" * 50, 20)), 20)


if __name__ == "__main__":
    unittest.main()
