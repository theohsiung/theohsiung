"""Area colors with all-time totals, under the chart."""

from collections import Counter

from areas import AREAS
from layout import CHART_BASE, CHART_X0, CHART_X1
from model import Entry
from palette import AREA_COLORS
from svg import el

COLUMNS = 3


def render_legend(entries: list[Entry]) -> str:
    totals = Counter(e.area for e in entries)
    shown = [a for a in AREAS if totals[a]]
    col = (CHART_X1 - CHART_X0) / COLUMNS
    out = []
    for i, area in enumerate(shown):
        x = CHART_X0 + (i % COLUMNS) * col
        y = CHART_BASE + 42 + (i // COLUMNS) * 18
        out.append(el("rect", x=f"{x:.1f}", y=y - 8, width=8, height=8, rx=2, fill=AREA_COLORS[area]))
        out.append(el("text", f"{area} {totals[area]}", x=f"{x + 14:.1f}", y=y, class_="tiny"))
    return "".join(out)
