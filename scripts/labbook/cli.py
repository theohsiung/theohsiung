"""Draw the lab notebook card: python3 scripts/labbook [--fixture FILE] [--out DIR]

Without --fixture it reads the user's merged pull requests from GitHub, using
GITHUB_TOKEN when it is set. It writes labbook-dark.svg and labbook-light.svg.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from card import render_card
from fetch import FetchError, fetch_items
from palette import PALETTES
from parse import parse_items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="labbook", description=__doc__.splitlines()[0])
    parser.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "theohsiung"))
    parser.add_argument("--fixture", type=Path, help="read search results from this JSON file instead of GitHub")
    parser.add_argument("--out", type=Path, default=Path("dist"))
    parser.add_argument("--now", type=datetime.fromisoformat, help="pretend it is this UTC time (for tests)")
    args = parser.parse_args(argv)

    if args.fixture:
        items = json.loads(args.fixture.read_text(encoding="utf-8"))["items"]
    else:
        try:
            items = fetch_items(args.user, os.environ.get("GITHUB_TOKEN"))
        except FetchError as err:
            print(f"labbook: {err}", file=sys.stderr)
            return 1
    entries = parse_items(items)
    now = (args.now or datetime.now(timezone.utc)).replace(tzinfo=timezone.utc)

    args.out.mkdir(parents=True, exist_ok=True)
    for theme, palette in PALETTES.items():
        path = args.out / f"labbook-{theme}.svg"
        path.write_text(render_card(entries, args.user, now, palette), encoding="utf-8")
        print(f"wrote {path}")
    return 0

