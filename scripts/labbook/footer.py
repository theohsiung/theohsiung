"""The summary line under the log."""

from datetime import date

from layout import H, LOG_X
from model import Entry
from svg import el


def summary(entries: list[Entry]) -> str:
    repos = len({e.repo for e in entries})
    noun = "repo" if repos == 1 else "repos"
    return f"{len(entries)} merged pull requests across {repos} {noun}"


def render_footer(entries: list[Entry], today: date) -> str:
    text = f"{summary(entries)} · regenerated {today.isoformat()} by scripts/labbook"
    return el("text", text, x=LOG_X, y=H - 26, class_="tiny")
