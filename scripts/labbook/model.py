"""The one record the card is drawn from: a merged pull request."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Entry:
    repo: str  # owner/name
    number: int
    title: str
    merged_at: datetime  # timezone-aware, UTC
    area: str

    @property
    def ref(self) -> str:
        return f"{self.repo}#{self.number}"
