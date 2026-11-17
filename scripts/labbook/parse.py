"""Turn GitHub search results into Entry records."""

from datetime import datetime

from areas import classify
from model import Entry


def parse_item(item: dict) -> Entry | None:
    """Return None for a pull request that was closed without merging."""
    merged = (item.get("pull_request") or {}).get("merged_at")
    if not merged:
        return None
    repo = item["repository_url"].split("/repos/", 1)[1]
    title = " ".join(item["title"].split())
    return Entry(repo, item["number"], title, datetime.fromisoformat(merged.replace("Z", "+00:00")), classify(title))


def parse_items(items: list[dict], exclude: tuple[str, ...] = ()) -> list[Entry]:
    """Newest first, one entry per pull request, without the repositories in `exclude`."""
    seen: set[str] = set()
    entries = []
    for item in items:
        entry = parse_item(item)
        if entry is None or entry.repo in exclude or entry.ref in seen:
            continue
        seen.add(entry.ref)
        entries.append(entry)
    return sorted(entries, key=lambda e: e.merged_at, reverse=True)
