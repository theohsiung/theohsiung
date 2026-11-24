"""The prompt line across the top of the card."""

from layout import LOG_RIGHT, PAD, W
from svg import el, esc


def render_header(user: str) -> str:
    prompt = (f'<text x="{PAD}" y="52" class="cmd"><tspan class="accent">$</tspan> '
              f"git log --merged --author={esc(user)}</text>")
    label = el("text", "lab notebook ■", x=W - PAD, y=52, class_="label", text_anchor="end")
    rule = el("line", x1=PAD, y1=70, x2=W - PAD, y2=70, class_="rule")
    split = el("line", x1=LOG_RIGHT + 30, y1=84, x2=LOG_RIGHT + 30, y2=276, class_="rule")
    return prompt + label + rule + split
