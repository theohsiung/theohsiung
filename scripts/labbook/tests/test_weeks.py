import unittest
from datetime import date, datetime, timezone

from model import Entry
from weeks import bucket, week_start


def at(day: date, area: str = "runtime") -> Entry:
    return Entry("o/r", 1, "t", datetime(day.year, day.month, day.day, tzinfo=timezone.utc), area)


class WeeksTest(unittest.TestCase):
    def test_week_starts_on_monday(self):
        self.assertEqual(week_start(date(2026, 11, 19)), date(2026, 11, 16))

    def test_last_bucket_is_this_week(self):
        buckets = bucket([], date(2026, 11, 17), weeks=4)
        self.assertEqual([d for d, _ in buckets][-1], date(2026, 11, 16))
        self.assertEqual(len(buckets), 4)

    def test_counts_by_area_and_drops_old(self):
        today = date(2026, 11, 17)
        entries = [at(date(2026, 11, 16)), at(date(2026, 11, 17), "perf"), at(date(2026, 1, 1))]
        buckets = bucket(entries, today, weeks=4)
        self.assertEqual(dict(buckets[-1][1]), {"runtime": 1, "perf": 1})
        self.assertEqual(sum(sum(c.values()) for _, c in buckets), 2)


if __name__ == "__main__":
    unittest.main()
