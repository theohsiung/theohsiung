"""The left half: the newest merged pull requests, one line each, typed in order."""

from datetime import datetime

from anim import Anims, appear
from layout import LOG_RIGHT, LOG_ROWS, LOG_STEP, LOG_X, LOG_Y, REF_CHARS, TITLE_CHARS
from model import Entry
from palette import AREA_COLORS
from svg import el, esc, star_path
from text import ago, truncate

ROW_START, ROW_STEP = 0.4, 0.5
HIDDEN = "opacity:0;transform:translateX(-10px)"
SHOWN = "opacity:1;transform:translateX(0)"


def render_row(entry: Entry, y: int, now: datetime) -> str:
    ref = truncate(f"{entry.repo.split('/')[-1]}#{entry.number}", REF_CHARS)
    return (el("path", d=star_path(LOG_X + 6, y - 4, 13), fill=AREA_COLORS[entry.area])
            + el("text", esc(ref), x=LOG_X + 20, y=y, class_="ref")
            + el("text", esc(truncate(entry.title, TITLE_CHARS)), x=LOG_X + 190, y=y, class_="title")
            + el("text", ago(entry.merged_at, now), x=LOG_RIGHT, y=y, class_="ref", text_anchor="end"))


def render_log(entries: list[Entry], now: datetime, anims: Anims) -> str:
    if not entries:
        return el("text", "no merged pull requests yet: run more experiments", x=LOG_X, y=LOG_Y, class_="title")
    rows = []
    shown = entries[:LOG_ROWS]
    for i, entry in enumerate(shown):
        y = LOG_Y + i * LOG_STEP
        row = render_row(entry, y, now)
        style = anims.attr(appear(ROW_START + i * ROW_STEP, hidden=HIDDEN, shown=SHOWN), base=SHOWN + ";")
        rows.append(f"<g {style}>{row}</g>")
    cursor_y = LOG_Y + len(shown) * LOG_STEP
    blink = [(0.0, "opacity:0")] + [
        (ROW_START + len(shown) * ROW_STEP + k * 0.5, "opacity:1" if k % 2 == 0 else "opacity:0") for k in range(14)
    ]
    cursor = el("path", d=star_path(LOG_X + 6, cursor_y - 5, 15), class_="cursor")
    rows.append(f'<g {anims.attr(blink, base="opacity:1;")}>{cursor}</g>')
    return "".join(rows)
