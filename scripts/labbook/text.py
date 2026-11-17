"""Fit text to the card."""

from datetime import datetime


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def ago(when: datetime, now: datetime) -> str:
    days = (now - when).days
    if days < 1:
        return "today"
    if days < 14:
        return f"{days}d ago"
    if days < 60:
        return f"{days // 7}w ago"
    if days < 730:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"
