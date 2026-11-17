"""Count merged pull requests per area for each of the last N weeks."""

from datetime import date, timedelta


def week_start(day: date) -> date:
    return day - timedelta(days=day.weekday())
