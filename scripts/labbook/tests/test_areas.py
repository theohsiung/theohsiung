import unittest

from areas import AREAS, RULES, classify


class ClassifyTest(unittest.TestCase):
    def test_real_titles(self):
        cases = {
            "[Feature] Model runtime: load NVFP4 Decision 3.0 packages": "runtime",
            "[Router] add pluggable jailbreak classifier backend": "security",
            "[Feature] Add vSR, a Claude Code plugin that runs the decision model inside the harness": "harness",
            "[Router] Dedup query-embedding inference on the cache-miss path": "perf",
            "[Router] Bound looper upstream response reads to a byte ceiling": "protocol",
            "feat: knowledge graph — lineage navigation index over the experience ledger": "research",
            "[Docs] Correct community meeting cadence wording": "upkeep",
            "[Router] Validate decision modelRefs and reject duplicate decision names": "routing",
            "Create rrr.py": "other",
        }
        for title, area in cases.items():
            with self.subTest(title=title):
                self.assertEqual(classify(title), area)

    def test_case_insensitive(self):
        self.assertEqual(classify("JAILBREAK"), "security")

    def test_rules_name_known_areas(self):
        self.assertTrue({area for area, _ in RULES} <= set(AREAS))


if __name__ == "__main__":
    unittest.main()
