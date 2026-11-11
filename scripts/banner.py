"""Generate assets/banner-{dark,light}.svg.

Run `python3 scripts/banner.py` after changing a palette or a scene below.

The banner alternates two scenes on one 20-second clock:

1. meta-research: an agent runs experiments on a liquid-cooling cold plate.
   Each experiment shows the design's heatmap (wine = hot, powder blue = cool)
   and adds a point to the thermal-resistance vs. pressure-drop chart; the
   Pareto frontier moves toward the lower left.
2. vSR: prompts pass through vLLM Semantic Router inside Claude Code. Each one
   goes to the right model, has its secret masked, or is held for you to
   confirm.

The heatmaps and chart are illustrative, so the banner shows no numbers.
"""

import math
from pathlib import Path

PALETTES = {
    "dark": {
        "bg": "#0d1117", "grid": "#1c2129", "panel": "#161b22", "track": "#30363d",
        "text": "#e6edf3", "muted": "#7d8590", "fin": "#ffffff",
        "wine": "#be123c", "wine_text": "#e8577a",
        "blue": "#a6cdec", "blue_line": "#a6cdec", "blue_text": "#c6dff2",
        "tag": ("#e8577a", "#b9d6ee"),
    },
    "light": {
        "bg": "#ffffff", "grid": "#e4e7eb", "panel": "#f6f8fa", "track": "#d0d7de",
        "text": "#1f2328", "muted": "#6e7781", "fin": "#ffffff",
        "wine": "#be123c", "wine_text": "#881337",
        "blue": "#a6cdec", "blue_line": "#4a78a6", "blue_text": "#4a78a6",
        "tag": ("#881337", "#4a78a6"),
    },
}
BAR = ("#881337", "#be123c", "#a6cdec")
HEAT = [(0.0, "#a6cdec"), (0.4, "#a78bb5"), (0.7, "#be123c"), (1.0, "#881337")]  # cool -> hot

CYCLE = 20.0
SCENE_A = (0.0, 9.4)  # visible window; each edge fades over FADE
SCENE_B = (10.0, 19.6)
FADE = 0.4
STAGE_X = 690

# Scene A: (hypothesis, thermal resistance, pressure drop, fin layout)
EXPERIMENTS = [
    ("baseline: straight fins", 0.80, 0.25, "straight"),
    ("baseline: pin fins", 0.45, 0.80, "pins"),
    ("stagger the pins", 0.38, 0.55, "stagger"),
    ("thinner, denser fins", 0.60, 0.70, "dense"),
    ("taper fins toward outlet", 0.50, 0.30, "taper"),
    ("staggered + tapered pins", 0.30, 0.42, "stagger_taper"),
]
HASHES = ["3c1a9e2", "a3f9c1e", "7be20d4", "e51c8a0", "0c4d7f2", "9d2b6f1"]
EXP_START, EXP_STEP = 0.6, 1.4

# Scene B: (prompt, what the model sees, route, (complexity, secrets, risk), log line)
REQUESTS = [
    ("rename this variable", "rename this variable", "fast", (0.15, 0.0, 0.05), "simple edit → fast model"),
    ("prove: no deadlock", "prove: no deadlock", "reasoning", (0.92, 0.0, 0.05), "hard reasoning → reasoning model"),
    ("deploy with sk-live-9f2a", "deploy with ••••••••", "fast", (0.30, 0.95, 0.20),
     "secret masked before Claude reads it → fast model"),
    ("Bash: rm -rf ~/", "Bash: rm -rf ~/", "held", (0.20, 0.0, 0.95), "risky Bash → held for you to confirm"),
]
DESTS = {"fast": ("fast model", 102), "reasoning": ("reasoning model", 162), "held": ("held · confirm?", 222)}
REQ_START, REQ_STEP = 10.4, 2.2
MID_Y = 162


class Anims:
    """Collects @keyframes on the shared CYCLE clock and returns the attributes that use them."""

    def __init__(self) -> None:
        self.rules: list[str] = []

    def attr(self, frames: list[tuple[float, str]], base: str = "", cls: str = "", timing: str = "") -> str:
        """`base` is the static style shown under prefers-reduced-motion."""
        frames = sorted(frames, key=lambda f: f[0])
        if frames[0][0] > 0:
            frames.insert(0, (0.0, frames[0][1]))
        if frames[-1][0] < CYCLE:
            frames.append((CYCLE, frames[-1][1]))
        name = f"k{len(self.rules)}"
        body = " ".join(f"{min(t, CYCLE) / CYCLE * 100:.3f}% {{ {css} }}" for t, css in frames)
        self.rules.append(f"@keyframes {name} {{ {body} }}")
        style = f"{base}animation-name:{name};" + (f"animation-timing-function:{timing};" if timing else "")
        classes = "a" + (f" {cls}" if cls else "")
        return f'class="{classes}" style="{style}"'


def window(t_on: float, t_off: float, fade: float = 0.3, on: str = "opacity:1", off: str = "opacity:0"):
    """Off, fade on at t_on, stay on, fade off at t_off."""
    if t_on <= 0:
        return [(0.0, on), (t_off, on), (min(t_off + fade, CYCLE), off)]
    return [(0.0, off), (t_on, off), (t_on + fade, on), (t_off, on), (min(t_off + fade, CYCLE), off)]


def heat_color(v: float) -> str:
    v = max(0.0, min(1.0, v))
    for (a, ca), (b, cb) in zip(HEAT, HEAT[1:]):
        if v <= b:
            f = (v - a) / (b - a)
            rgb = [round(int(ca[i:i + 2], 16) * (1 - f) + int(cb[i:i + 2], 16) * f) for i in (1, 3, 5)]
            return "#%02x%02x%02x" % tuple(rgb)
    return HEAT[-1][1]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- scene A: meta-research
HX, HY, COLS, ROWS, CELL = STAGE_X, 86, 10, 8, 19
PX0, PX1, PY0, PY1 = 948, 1150, 238, 86


def chart_xy(r: float, dp: float) -> tuple[float, float]:
    return PX0 + (r - 0.2) / 0.7 * (PX1 - PX0), PY0 - (dp - 0.15) / 0.75 * (PY0 - PY1)


def fins(layout: str, p: dict) -> str:
    w, h = COLS * CELL, ROWS * CELL
    out = []
    line = f'stroke="{p["fin"]}" stroke-opacity=".45" stroke-linecap="round"'
    if layout in ("straight", "dense"):
        n, sw = (4, 2.5) if layout == "straight" else (7, 1.4)
        for k in range(1, n + 1):
            y = HY + h * k / (n + 1)
            out.append(f'<line x1="{HX + 8}" y1="{y:.1f}" x2="{HX + w - 8}" y2="{y:.1f}" {line} stroke-width="{sw}"/>')
    elif layout == "taper":
        for k in range(1, 5):
            y0 = HY + h * k / 5
            y1 = HY + h / 2 + (y0 - HY - h / 2) * 0.55
            out.append(f'<line x1="{HX + 8}" y1="{y0:.1f}" x2="{HX + w - 8}" y2="{y1:.1f}" {line} stroke-width="2.2"/>')
    else:
        stagger = layout.startswith("stagger")
        for row in range(4):
            for col in range(6):
                x = HX + 18 + col * 31 + (15 if stagger and row % 2 else 0)
                y = HY + 22 + row * 36
                r = 3.8 - col * 0.4 if layout == "stagger_taper" else 3.4
                if x < HX + w - 6:
                    out.append(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="{p["fin"]}" fill-opacity=".5"/>')
    return "".join(out)


def pareto(points: list[tuple[float, float]], upto: int) -> list[int]:
    """Indices of the non-dominated points among points[0..upto], by rising thermal resistance."""
    idx = range(upto + 1)
    front = [i for i in idx if not any(j != i and points[j][0] <= points[i][0] and points[j][1] <= points[i][1] for j in idx)]
    return sorted(front, key=lambda i: points[i][0])


def scene_a(p: dict, an: Anims) -> str:
    _, a_off = SCENE_A
    times = [EXP_START + EXP_STEP * i for i in range(len(EXPERIMENTS))]
    last = len(EXPERIMENTS) - 1
    points = [(r, dp) for _, r, dp, _ in EXPERIMENTS]
    out = []

    # heatmap of the design under test; the hot spot scales with thermal resistance
    for i, (_, r, _dp, layout) in enumerate(EXPERIMENTS):
        cells = []
        for row in range(ROWS):
            for col in range(COLS):
                cx, cy = (col + 0.5) / COLS, (row + 0.5) / ROWS
                spot = math.exp(-((cx - 0.58) ** 2 + (cy - 0.5) ** 2) / (2 * 0.22 ** 2))
                t = (r * (0.35 + 0.65 * spot) + 0.18 * r * cx) / 0.9
                cells.append(f'<rect x="{HX + col * CELL}" y="{HY + row * CELL}" width="{CELL - 1}" '
                             f'height="{CELL - 1}" rx="2" fill="{heat_color(t)}"/>')
        t_off = times[i + 1] if i < last else a_off
        style = an.attr(window(times[i], t_off, 0.35), base=f"opacity:{1 if i == last else 0};")
        out.append(f'<g {style}>{"".join(cells)}{fins(layout, p)}</g>')
    out.append(f'<text x="{HX}" y="256" class="small">cold plate</text>'
               f'<text x="{HX + COLS * CELL}" y="256" class="small" text-anchor="end">'
               f'<tspan fill="{p["blue"]}">■</tspan> cool  <tspan fill="{p["wine"]}">■</tspan> hot</text>')

    # chart axes
    mid_y = (PY0 + PY1) / 2
    out.append(f'<path d="M{PX0} {PY1 - 4} V{PY0} H{PX1 + 4}" fill="none" stroke="{p["track"]}" stroke-width="1.5"/>'
               f'<text x="{(PX0 + PX1) / 2}" y="256" class="small" text-anchor="middle">thermal resistance →</text>'
               f'<text x="{PX0 - 10}" y="{mid_y}" class="small" text-anchor="middle" '
               f'transform="rotate(-90 {PX0 - 10} {mid_y})">pressure drop →</text>'
               f'<text x="{PX0 + 6}" y="{PY0 - 6}" class="small">↙ better</text>')

    # Pareto frontier after each experiment: a staircase, with the region it dominates shaded
    dominated_at: dict[int, float] = {}
    for k in range(len(points)):
        front = pareto(points, k)
        for i in range(k + 1):
            if i not in front:
                dominated_at.setdefault(i, times[k] + 0.3)
        xy = [chart_xy(*points[i]) for i in front]
        stairs = f"M{xy[0][0]:.1f} {PY1} V{xy[0][1]:.1f}"
        for x, y in xy[1:]:
            stairs += f" H{x:.1f} V{y:.1f}"
        stairs += f" H{PX1}"
        t_off = times[k + 1] + 0.3 if k < last else a_off
        style = an.attr(window(times[k] + 0.3, t_off, 0.35), base=f"opacity:{1 if k == last else 0};")
        out.append(f'<g {style}><path d="{stairs} V{PY1} Z" fill="{p["blue"]}" fill-opacity=".12"/>'
                   f'<path d="{stairs}" fill="none" stroke="{p["blue_line"]}" stroke-width="1.5" stroke-dasharray="4 3"/></g>')

    # experiment points: filled while on the frontier, hollow once dominated
    on = f"fill:{p['blue']};stroke:{p['blue_line']}"
    off = f"fill:{p['bg']};stroke:{p['muted']}"
    for i, (r, dp) in enumerate(points):
        x, y = chart_xy(r, dp)
        born = times[i] + 0.15
        dead_on_arrival = dominated_at.get(i, CYCLE) <= born + 0.4
        first = off if dead_on_arrival else on
        frames = [(0.0, f"opacity:0;transform:scale(.2);{first}"), (born, f"opacity:0;transform:scale(.2);{first}"),
                  (born + 0.35, f"opacity:1;transform:scale(1.6);{first}"), (born + 0.6, f"opacity:1;transform:scale(1);{first}")]
        if i in dominated_at and not dead_on_arrival:
            frames += [(dominated_at[i], f"opacity:1;transform:scale(1);{on}"),
                       (dominated_at[i] + 0.4, f"opacity:1;transform:scale(1);{off}")]
        final = off if i in dominated_at else on
        style = an.attr(frames, base=f"opacity:1;{final};", cls="fb")
        out.append(f'<circle {style} cx="{x:.1f}" cy="{y:.1f}" r="5" stroke-width="1.8"/>')

    # experiment log
    for i, (hyp, *_rest) in enumerate(EXPERIMENTS):
        kept = dominated_at.get(i, CYCLE) > times[i] + 0.6
        verdict = (f'<tspan fill="{p["blue_text"]}">✓ frontier</tspan>' if kept
                   else f'<tspan fill="{p["wine_text"]}">✗ dominated</tspan>')
        t_off = times[i + 1] - 0.25 if i < last else a_off
        style = an.attr(window(times[i], t_off, 0.25), base=f"opacity:{1 if i == last else 0};", cls="log")
        out.append(f'<text {style} x="{STAGE_X}" y="292">exp {i + 1:02d} · {esc(hyp)} → {verdict}'
                   f' · commit {HASHES[i]}</text>')
    return "".join(out)


# ---------------------------------------------------------------- scene B: vSR
RX0, RX1, RY0, RY1 = 880, 988, 86, 238
METERS = ["complexity", "secrets", "risk"]


def chip(x: float, y: float, text: str, size: int, stroke: str, p: dict) -> str:
    w, h = len(text) * size * 0.6 + 18, size + 12
    return (f'<rect x="{x}" y="{y - h / 2}" width="{w:.0f}" height="{h}" rx="{h / 2}" fill="{p["panel"]}" '
            f'stroke="{stroke}" stroke-width="1.4"/>'
            f'<text x="{x + 9}" y="{y + size * 0.35:.1f}" class="chip" style="font-size:{size}px">{esc(text)}</text>')


def scene_b(p: dict, an: Anims) -> str:
    starts = [REQ_START + REQ_STEP * i for i in range(len(REQUESTS))]

    def line(route: str) -> str:
        return p["wine_text"] if route == "held" else p["blue_line"]

    out = []
    # destinations light up as a request lands
    for key, (label, cy) in DESTS.items():
        frames = [(0.0, f"stroke:{p['track']}")]
        for t, req in zip(starts, REQUESTS):
            if req[2] == key:
                frames += [(t + 1.45, f"stroke:{p['track']}"), (t + 1.6, f"stroke:{line(key)}"),
                           (t + 2.0, f"stroke:{line(key)}"), (t + 2.2, f"stroke:{p['track']}")]
        out.append(f'<rect {an.attr(frames)} x="1006" y="{cy - 24}" width="160" height="48" rx="8" '
                   f'fill="{p["panel"]}" stroke="{p["track"]}" stroke-width="1.4"/>'
                   f'<text x="1016" y="{cy - 8}" class="small" style="fill:{line(key)}">{label}</text>')

    # router: outline takes the route's color while it decides; meters show the three signals
    frames = [(0.0, f"stroke:{p['track']}")]
    for t, req in zip(starts, REQUESTS):
        c = line(req[2])
        frames += [(t + 0.6, f"stroke:{p['track']}"), (t + 0.8, f"stroke:{c}"), (t + 1.5, f"stroke:{c}"), (t + 1.8, f"stroke:{p['track']}")]
    out.append(f'<rect {an.attr(frames)} x="{RX0}" y="{RY0}" width="{RX1 - RX0}" height="{RY1 - RY0}" rx="12" '
               f'fill="{p["panel"]}" stroke="{p["track"]}" stroke-width="1.6"/>'
               f'<text x="{(RX0 + RX1) / 2}" y="{RY0 + 24}" class="router" text-anchor="middle">vSR</text>')
    for m, name in enumerate(METERS):
        y = RY0 + 50 + m * 34
        frames = [(0.0, "transform:scaleX(.001)")]
        for t, req in zip(starts, REQUESTS):
            v = max(req[3][m], 0.001)
            frames += [(t + 0.65, "transform:scaleX(.001)"), (t + 1.05, f"transform:scaleX({v})"),
                       (t + 1.7, f"transform:scaleX({v})"), (t + 2.0, "transform:scaleX(.001)")]
        bar = f'x="{RX0 + 10}" y="{y + 6}" width="{RX1 - RX0 - 20}" height="5" rx="2.5"'
        out.append(f'<text x="{RX0 + 10}" y="{y}" class="tiny">{name}</text><rect {bar} fill="{p["track"]}"/>'
                   f'<rect {an.attr(frames, cls="fl")} {bar} fill="{p["wine"] if name == "risk" else p["blue"]}"/>')

    # each request: the prompt slides into the router, and what the model sees slides out to its route
    for t, (prompt, seen, route, _levels, log) in zip(starts, REQUESTS):
        frames = [(0.0, "opacity:0;transform:translateX(-14px)"), (t, "opacity:0;transform:translateX(-14px)"),
                  (t + 0.3, "opacity:1;transform:translateX(0)"), (t + 0.6, "opacity:1;transform:translateX(0)"),
                  (t + 0.95, "opacity:0;transform:translateX(150px)")]
        out.append(f'<g {an.attr(frames, base="opacity:0;")}>{chip(STAGE_X, MID_Y, prompt, 11, p["track"], p)}</g>')

        move = f"translate(24px,{DESTS[route][1] + 10 - MID_Y}px)"
        frames = [(0.0, "opacity:0;transform:translate(0,0)"), (t + 1.05, "opacity:0;transform:translate(0,0)"),
                  (t + 1.2, "opacity:1;transform:translate(0,0)"), (t + 1.6, f"opacity:1;transform:{move}"),
                  (t + 2.0, f"opacity:1;transform:{move}"), (t + 2.15, f"opacity:0;transform:{move}")]
        out.append(f'<g {an.attr(frames, base="opacity:0;")}>{chip(RX1 + 4, MID_Y, seen, 10, line(route), p)}</g>')

        color = p["wine_text"] if route == "held" else p["blue_text"]
        style = an.attr(window(t + 1.1, t + 2.05, 0.2), base="opacity:0;", cls="log")
        out.append(f'<text {style} x="{STAGE_X}" y="292"><tspan fill="{color}">{esc(log)}</tspan></text>')
    return "".join(out)


# ---------------------------------------------------------------- banner
def typed(command: str, start: float, p: dict, an: Anims) -> str:
    """A command line typed out from `start`, revealed by a cover that shrinks one character at a time."""
    width = len(command) * 8.4 + 8
    frames = [(0.0, "transform:scaleX(1)"), (start, "transform:scaleX(1)"), (start + 0.9, "transform:scaleX(0)")]
    cover = an.attr(frames, base="transform:scaleX(0);", cls="fr", timing=f"steps({len(command)})")
    return (f'<text x="66" y="262" class="mono">{esc(command)}</text>'
            f'<rect {cover} x="60" y="246" width="{width:.0f}" height="22" fill="{p["bg"]}"/>')


def scene_header(title: str, subtitle: str, active: int, p: dict) -> str:
    dots = "".join(f'<circle cx="{1150 + k * 14}" cy="46" r="4" fill="{p["blue"] if k == active else p["track"]}"/>'
                   for k in range(2))
    return f'<text x="{STAGE_X}" y="50" class="title">{title}<tspan class="subtitle"> · {subtitle}</tspan></text>{dots}'


def render(p: dict) -> str:
    an = Anims()
    a_style = an.attr(window(*SCENE_A, FADE), base="opacity:1;")
    b_style = an.attr(window(*SCENE_B, FADE), base="opacity:0;")
    a = (scene_header("meta-research", "an agent optimizes a cold plate", 0, p)
         + typed("$ meta-research run water_cooling", SCENE_A[0] + 0.2, p, an) + scene_a(p, an))
    b = (scene_header("vSR", "vLLM Semantic Router inside Claude Code", 1, p)
         + typed("$ claude --plugin vsr", SCENE_B[0] + 0.2, p, an) + scene_b(p, an))
    keyframes = "\n      ".join(an.rules)
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    sans = '-apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="1200" height="320" role="img" aria-labelledby="t d">
  <title id="t">Theo Hsiung</title>
  <desc id="d">AI for Science, LLM systems and agentic infrastructure. Two alternating scenes: an agent optimizing a liquid-cooling cold plate, pushing the Pareto frontier of thermal resistance and pressure drop; and vLLM Semantic Router inside Claude Code sending each prompt to the right model, masking a secret, and holding a risky Bash command.</desc>
  <!-- Generated by scripts/banner.py; edit the palette and scenes there, not here. -->
  <defs>
    <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{p["grid"]}"/></pattern>
    <clipPath id="round"><rect width="1200" height="320" rx="16"/></clipPath>
    <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{BAR[0]}"/><stop offset=".5" stop-color="{BAR[1]}"/><stop offset="1" stop-color="{BAR[2]}"/></linearGradient>
    <linearGradient id="tag" x1="0" x2="1"><stop offset="0" stop-color="{p["tag"][0]}"/><stop offset="1" stop-color="{p["tag"][1]}"/></linearGradient>
    <style>
      .name {{ font: 700 64px {sans}; fill: {p["text"]}; letter-spacing: -1px; }}
      .tag {{ font: 600 22px {sans}; fill: url(#tag); }}
      .sub {{ font: 400 16px {sans}; fill: {p["muted"]}; }}
      .mono {{ font: 500 14px {mono}; fill: {p["muted"]}; }}
      .title {{ font: 700 13px {mono}; fill: {p["text"]}; }}
      .subtitle {{ font-weight: 400; fill: {p["muted"]}; }}
      .small {{ font: 500 11px {mono}; fill: {p["muted"]}; }}
      .tiny {{ font: 500 10px {mono}; fill: {p["muted"]}; }}
      .log {{ font: 500 12px {mono}; fill: {p["muted"]}; }}
      .chip {{ font-family: {mono}; font-weight: 500; fill: {p["text"]}; }}
      .router {{ font: 700 14px {mono}; fill: {p["blue_text"]}; }}

      .a {{ animation-duration: {CYCLE:g}s; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
      .fb {{ transform-box: fill-box; transform-origin: center; }}
      .fl {{ transform-box: fill-box; transform-origin: left center; }}
      .fr {{ transform-box: fill-box; transform-origin: right center; }}
      {keyframes}

      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    </style>
  </defs>

  <rect width="1200" height="320" rx="16" fill="{p["bg"]}"/>
  <rect width="1200" height="320" rx="16" fill="url(#dots)"/>
  <rect width="1200" height="4" fill="url(#bar)" clip-path="url(#round)"/>

  <text x="64" y="122" class="name">Theo Hsiung</text>
  <text x="66" y="164" class="tag">AI for Science · LLM Systems · Agentic Infra</text>
  <text x="66" y="196" class="sub">Associate Research Scientist, vLLM Semantic Router · Delta Electronics · Taiwan</text>

  <g {a_style}>{a}</g>
  <g {b_style}>{b}</g>
</svg>
'''


if __name__ == "__main__":
    assets = Path(__file__).resolve().parent.parent / "assets"
    for theme, palette in PALETTES.items():
        (assets / f"banner-{theme}.svg").write_text(render(palette), encoding="utf-8")
        print(f"wrote assets/banner-{theme}.svg")
