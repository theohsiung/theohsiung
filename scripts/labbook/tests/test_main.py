import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from cli import main
from helpers import FIXTURE


class MainTest(unittest.TestCase):
    def test_fixture_writes_both_themes(self):
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()):
            code = main(["--fixture", str(FIXTURE), "--out", out, "--now", "2026-11-17T12:00:00"])
            self.assertEqual(code, 0)
            names = sorted(p.name for p in Path(out).iterdir())
        self.assertEqual(names, ["labbook-dark.svg", "labbook-light.svg"])

    def test_profile_repo_is_excluded_by_default(self):
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()):
            main(["--fixture", str(FIXTURE), "--out", out, "--user", "theohsiung"])
            text = (Path(out) / "labbook-dark.svg").read_text(encoding="utf-8")
        self.assertIn("8 merged pull requests", text)


if __name__ == "__main__":
    unittest.main()
