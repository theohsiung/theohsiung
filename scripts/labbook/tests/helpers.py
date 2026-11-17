"""Shared test inputs: the recorded search fixture and a fixed clock."""

import json
from datetime import datetime, timezone
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "search.json"
NOW = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)


def items() -> list[dict]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["items"]
