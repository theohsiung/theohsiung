import unittest
from datetime import date

from weeks import week_start


class WeeksTest(unittest.TestCase):
    def test_week_starts_on_monday(self):
        self.assertEqual(week_start(date(2026, 11, 19)), date(2026, 11, 16))


if __name__ == "__main__":
    unittest.main()
