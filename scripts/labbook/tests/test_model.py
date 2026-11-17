import unittest
from datetime import datetime, timezone

from model import Entry


class EntryTest(unittest.TestCase):
    def test_ref_joins_repo_and_number(self):
        entry = Entry("vllm-project/semantic-router", 6113, "t", datetime.now(timezone.utc), "runtime")
        self.assertEqual(entry.ref, "vllm-project/semantic-router#6113")


if __name__ == "__main__":
    unittest.main()
