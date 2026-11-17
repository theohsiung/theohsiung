"""Count merged pull requests per area for each of the last N weeks."""

from collections import Counter
from datetime import date, timedelta

from model import Entry


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())


def bucket(entries: list[Entry], today: date, weeks: int = 12) -> list[tuple[date, Counter]]:
    """Oldest week first; the last bucket is the week that contains `today`."""
    first = week_start(today) - timedelta(weeks=weeks - 1)
    buckets = [(first + timedelta(weeks=i), Counter()) for i in range(weeks)]
    for entry in entries:
        index = (week_start(entry.merged_at.date()) - first).days // 7
        if 0 <= index < weeks:
            buckets[index][1][entry.area] += 1
    return buckets
