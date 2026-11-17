"""The right half: merged pull requests per week, stacked by area."""

from collections import Counter
from datetime import date

from anim import Anims, appear
from areas import AREAS
from layout import CHART_BASE, CHART_TOP, CHART_X0, CHART_X1
from palette import AREA_COLORS
from svg import el

BAR_START, BAR_STEP = 0.6, 0.12


def render_chart(buckets: list[tuple[date, Counter]], anims: Anims) -> str:
    slot = (CHART_X1 - CHART_X0) / len(buckets)
    width = slot * 0.62
    peak = max([sum(c.values()) for _, c in buckets] + [1])
    unit = (CHART_BASE - CHART_TOP) / peak
    out = [el("text", "merged per week, by area", x=CHART_X0, y=CHART_TOP - 12, class_="small")]
    for i, (_, counts) in enumerate(buckets):
        x = CHART_X0 + i * slot + (slot - width) / 2
        out.append(el("rect", x=f"{x:.1f}", y=CHART_TOP, width=f"{width:.1f}", height=CHART_BASE - CHART_TOP,
                      rx=3, class_="track"))
        y = CHART_BASE
        segments = []
        for area in AREAS:
            h = counts.get(area, 0) * unit
            if h:
                y -= h
                segments.append(el("rect", x=f"{x:.1f}", y=f"{y:.1f}", width=f"{width:.1f}", height=f"{h:.1f}",
                                   fill=AREA_COLORS[area]))
        if segments:
            grow = appear(BAR_START + i * BAR_STEP, hidden="transform:scaleY(0)", shown="transform:scaleY(1)")
            out.append(f'<g {anims.attr(grow, base="transform:scaleY(1);", cls="grow")}>{"".join(segments)}</g>')
    out.append(el("text", f"{len(buckets)}w ago", x=CHART_X0, y=CHART_BASE + 18, class_="tiny"))
    out.append(el("text", "this week", x=CHART_X1, y=CHART_BASE + 18, class_="tiny", text_anchor="end"))
    return "".join(out)
