import unittest
from datetime import timezone

from helpers import items
from parse import parse_item, parse_items


class ParseTest(unittest.TestCase):
    def test_item_fields(self):
        entry = parse_item(items()[1])
        self.assertEqual(entry.ref, "vllm-project/semantic-router#6113")
        self.assertEqual(entry.area, "runtime")
        self.assertEqual(entry.merged_at.tzinfo, timezone.utc)

    def test_unmerged_is_skipped(self):
        self.assertIsNone(parse_item(items()[-1]))

    def test_duplicates_are_dropped(self):
        refs = [e.ref for e in parse_items(items())]
        self.assertEqual(len(refs), len(set(refs)))
        self.assertEqual(len(refs), 9)

    def test_excluded_repos_are_dropped(self):
        refs = [e.ref for e in parse_items(items(), exclude=("theohsiung/theohsiung",))]
        self.assertNotIn("theohsiung/theohsiung#8", refs)
        self.assertEqual(len(refs), 8)

    def test_newest_first(self):
        dates = [e.merged_at for e in parse_items(items())]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_whitespace_in_titles_is_collapsed(self):
        item = dict(items()[1], title="  two   spaces\n")
        self.assertEqual(parse_item(item).title, "two spaces")


if __name__ == "__main__":
    unittest.main()
