"""Generate assets/banner-{dark,light}.svg.

Run `python3 scripts/banner.py` after changing a palette or a scene below.

The banner alternates three scenes on one 30-second clock:

1. meta-research: an agent runs experiments on a liquid-cooling cold plate.
   Each experiment shows the design's heatmap (orange = hot, teal = cool)
   and adds a point to the thermal-resistance vs. pressure-drop chart; the
   Pareto frontier moves toward the lower left.
2. vSR: prompts pass through vLLM Semantic Router inside Claude Code. Each one
   goes to the right model, has its secret masked, or is held for you to
   confirm.
3. orbit: a concept scene. Compute goes where the data is: raw imagery is
   processed on an orbital node and only the result comes down, heavy
   training goes to ground GPUs, and a task with no ground link waits for
   the next pass.

The heatmaps, chart and orbit scene are illustrative, so the banner shows no numbers.
"""

import math
from pathlib import Path

PALETTES = {
    # Colors sampled from the Semantic Router Labs launch video: near-black ink, orange-red #ff5b2b,
    # amber for "fast" (#ffd183), teal for "deep" (#97dbd9), cream #e8e6e3, periwinkle and peach.
    "dark": {
        "mode": "dark",
        "bg": "#05080e", "bg2": "#0f0e15", "panel": "#0c1119", "track": "#2b2e3a",
        "text": "#f2efe9", "muted": "#9b9aa3", "fin": "#ffffff", "star_op": "0.7", "pglow": "0.30",
        "hot": "#ff5b2b", "hot_text": "#ff8a62", "amber": "#ffd183",         # orange: hot, or held for you
        "cool": "#97dbd9", "cool_line": "#97dbd9", "cool_text": "#b8ebe9",   # teal: cool, or routed
        "violet": "#869bdc", "tag": ("#ffd183", "#ff7a4a"), "name": ("#ffffff", "#f2e6d8"),
        "ramp": [(0.0, "#3a1520"), (0.35, "#a8431f"), (0.65, "#ff5b2b"), (0.85, "#ff9a6a"), (1.0, "#ffe0c2")],
        "ring": ["#ffd183", "#ffe3b0", "#ffd183", "#ff9a6a"],
        "glows": [(1010, 30, 340, "#a8431f", 0.42), (230, 330, 300, "#5a2a3a", 0.40),
                  (1190, 310, 240, "#ff5b2b", 0.20), (600, 100, 170, "#ff7a4a", 0.16)],
    },
    "light": {
        "mode": "light",
        "bg": "#e8e6e3", "bg2": "#ebe4d4", "panel": "#f4f2ed", "track": "#c9c6bd",
        "text": "#14151a", "muted": "#66655f", "fin": "#ffffff", "star_op": "0.3", "pglow": "0.16",
        "hot": "#e5421a", "hot_text": "#c93410", "amber": "#b87a1c",
        "cool": "#7dc2c0", "cool_line": "#3f9a98", "cool_text": "#256b69",
        "violet": "#6f84c8", "tag": ("#d63a15", "#a82c0f"), "name": ("#14151a", "#14151a"),
        "ramp": [(0.0, "#a84a36"), (0.35, "#d6502a"), (0.65, "#ff7a4a"), (0.85, "#ffb08a"), (1.0, "#ffe6cf")],
        "ring": ["#d98a24", "#f0b25e", "#d98a24", "#ff7a4a"],
        "glows": [(930, 160, 330, "#f4b98f", 0.55), (200, 300, 260, "#b9c8e8", 0.45), (1100, 40, 220, "#f2b98f", 0.35)],
    },
}
BAR = ("#ff5b2b", "#ffd183", "#97dbd9")
HEAT = [(0.0, "#7dc2c0"), (0.3, "#8fb0d8"), (0.52, "#e0a994"), (0.75, "#ff7a4a"), (1.0, "#ff5b2b")]  # cool -> hot

CYCLE = 30.0
SCENE_A = (0.0, 9.4)  # visible window; each edge fades over FADE
SCENE_B = (10.0, 19.6)
SCENE_C = (20.0, 29.6)
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
               f'<tspan fill="{HEAT[0][1]}">■</tspan> cool  <tspan fill="{HEAT[-1][1]}">■</tspan> hot</text>')

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
        out.append(f'<g {style}><path d="{stairs} V{PY1} Z" fill="{p["cool"]}" fill-opacity=".12"/>'
                   f'<path d="{stairs}" fill="none" stroke="{p["cool_line"]}" stroke-width="1.5" stroke-dasharray="4 3"/></g>')

    # experiment points: filled while on the frontier, hollow once dominated
    on = f"fill:{p['cool']};stroke:{p['cool_line']}"
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
        verdict = (f'<tspan fill="{p["cool_text"]}">✓ frontier</tspan>' if kept
                   else f'<tspan fill="{p["hot_text"]}">✗ dominated</tspan>')
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
        return p["hot_text"] if route == "held" else p["cool_line"]

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
                   f'<rect {an.attr(frames, cls="fl")} {bar} fill="{p["hot"] if name == "risk" else p["cool"]}"/>')

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

        color = p["hot_text"] if route == "held" else p["cool_text"]
        style = an.attr(window(t + 1.1, t + 2.05, 0.2), base="opacity:0;", cls="log")
        out.append(f'<text {style} x="{STAGE_X}" y="292"><tspan fill="{color}">{esc(log)}</tspan></text>')
    return "".join(out)


# ---------------------------------------------------------------- scene C: orbit (concept)
ORBIT = ((692, 150), (930, 20), (1168, 150))      # quadratic Bezier: start, control, end
HORIZON = ((692, 262), (930, 214), (1168, 262))
ROUTER = (930, 160)
STARS = [(712, 78, 1.2), (748, 64, 1.0), (812, 70, 1.4), (868, 58, 1.0), (1010, 66, 1.2), (1064, 62, 1.4),
         (1118, 82, 1.0), (1152, 70, 1.2), (724, 176, 1.0), (760, 200, 1.2), (1135, 178, 1.0), (1160, 205, 1.4),
         (850, 198, 1.0), (1040, 196, 1.0)]

# (task, route, caption). A route is the node that does the work, or "queue" when there is no ground link.
TASKS = [
    ("classify raw imagery", "orbit", "raw data stays up: process in orbit, downlink only the result"),
    ("fine-tune the model", "gpu", "heavy compute → ground GPUs"),
    ("no ground link", "queue", "no link window → hold until the next pass"),
]
TASK_START, TASK_STEP = 20.4, 3.1


def bez(arc: tuple, t: float) -> tuple[float, float]:
    (x0, y0), (cx, cy), (x1, y1) = arc
    u = 1 - t
    return u * u * x0 + 2 * u * t * cx + t * t * x1, u * u * y0 + 2 * u * t * cy + t * t * y1


def arc_path(arc: tuple) -> str:
    (x0, y0), (cx, cy), (x1, y1) = arc
    return f"M{x0} {y0} Q{cx} {cy} {x1} {y1}"


def lit(base: str, on: str, windows: list[tuple[float, float]], extra_base: str = "", extra_on: str = "") -> list:
    """Keyframes for a node that takes a lit style during each (t_on, t_off) window."""
    frames = [(0.0, f"{base};{extra_base}")]
    for t_on, t_off in windows:
        frames += [(t_on, f"{base};{extra_base}"), (t_on + 0.2, f"{on};{extra_on}"), (t_off, f"{on};{extra_on}"),
                   (t_off + 0.3, f"{base};{extra_base}")]
    return frames


def scene_c(p: dict, an: Anims) -> str:
    starts = [TASK_START + TASK_STEP * i for i in range(len(TASKS))]
    sats = [bez(ORBIT, t) for t in (0.2, 0.5, 0.8)]
    gpu, station = bez(HORIZON, 0.2), bez(HORIZON, 0.82)
    main_sat = sats[1]
    rx, ry = ROUTER
    out = [f'<defs><linearGradient id="earth" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["panel"]}" stop-opacity="1"/>'
           f'<stop offset="1" stop-color="{p["panel"]}" stop-opacity="0"/></linearGradient></defs>']

    # sky and ground
    out += [f'<circle cx="{x}" cy="{y}" r="{r * 1.3:.1f}" fill="{p["text"]}" opacity="{p["star_op"]}"/>' for x, y, r in STARS]
    out.append(f'<path d="{arc_path(HORIZON)} V320 H692 Z" fill="url(#earth)"/>'
               f'<path d="{arc_path(HORIZON)}" fill="none" stroke="{p["cool_line"]}" stroke-width="7" opacity=".16"/>'
               f'<path d="{arc_path(HORIZON)}" fill="none" stroke="{p["cool_line"]}" stroke-width="1.6" opacity=".85"/>'
               f'<path d="{arc_path(ORBIT)}" fill="none" stroke="{p["violet"]}" stroke-opacity=".7" stroke-width="1.6" stroke-dasharray="3 5"/>'
               f'<text x="700" y="126" class="tiny">orbit</text><text x="700" y="248" class="tiny">ground</text>')

    # orbit nodes drift a little along the arc; the one that does the work lights up
    work = {"orbit": starts[0]}
    for i, (x, y) in enumerate(sats):
        drift = [(0.0, "transform:translate(0,0)"), (CYCLE / 2, "transform:translate(10px,0)"), (CYCLE, "transform:translate(0,0)")]
        windows = [(work["orbit"] + 1.4, work["orbit"] + 2.9)] if i == 1 else []
        body = lit(f"fill:{p['muted']}", f"fill:{p['cool']}", windows) if windows else [(0.0, f"fill:{p['muted']}")]
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) scale(1.7)"><g {an.attr(drift)}>'
                   f'<rect x="-17" y="-2.5" width="9" height="5" rx="1" fill="{p["panel"]}" stroke="{p["track"]}"/>'
                   f'<rect x="8" y="-2.5" width="9" height="5" rx="1" fill="{p["panel"]}" stroke="{p["track"]}"/>'
                   f'<rect {an.attr(body)} x="-6" y="-4" width="12" height="8" rx="2" stroke="{p["track"]}"/></g></g>')

    # ground nodes
    for name, (x, y), label, t_work in (("gpu", gpu, "GPUs", starts[1] + 1.4), ("station", station, "station", starts[0] + 2.1)):
        frames = lit(f"stroke:{p['track']}", f"stroke:{p['cool_line']}", [(t_work, t_work + 1.3)])
        out.append(f'<g transform="translate({x:.1f} {y - 11:.1f}) scale(1.35)"><rect {an.attr(frames)} x="-12" y="-7" width="24" height="14" rx="3" '
                   f'fill="{p["panel"]}" stroke-width="1.6"/>'
                   + ('<path d="M-6 -2 H6 M-6 2 H6" stroke="' + p["muted"] + '" stroke-width="1.4" stroke-linecap="round"/>' if name == "gpu"
                      else '<path d="M-6 3 Q0 -9 6 3" fill="none" stroke="' + p["muted"] + '" stroke-width="1.4"/>')
                   + f'</g><text x="{x:.1f}" y="{y + 16:.1f}" class="tiny" text-anchor="middle">{label}</text>')

    # router: outline takes the route's color while it decides
    frames = [(0.0, f"stroke:{p['track']}")]
    for t, (_, route, _) in zip(starts, TASKS):
        c = p["hot"] if route == "queue" else p["cool_line"]
        end = t + (2.2 if route == "queue" else 1.5)
        frames += [(t + 0.6, f"stroke:{p['track']}"), (t + 0.8, f"stroke:{c}"), (end, f"stroke:{c}"), (end + 0.3, f"stroke:{p['track']}")]
    out.append(f'<rect {an.attr(frames)} x="{rx - 35}" y="{ry - 17}" width="70" height="34" rx="9" fill="{p["panel"]}" stroke-width="1.6"/>'
               f'<text x="{rx}" y="{ry + 4}" class="router" text-anchor="middle">vSR</text>')

    def beam(a: tuple, b: tuple, t0: float, color: str) -> str:
        d = f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}"
        frames = [(0.0, "opacity:0;stroke-dashoffset:1"), (t0, "opacity:0;stroke-dashoffset:1"), (t0 + 0.02, "opacity:1;stroke-dashoffset:1"),
                  (t0 + 0.5, "opacity:1;stroke-dashoffset:0"), (t0 + 1.3, "opacity:1;stroke-dashoffset:0"), (t0 + 1.6, "opacity:0;stroke-dashoffset:0")]
        return (f'<path {an.attr(frames, base="opacity:0;")} d="{d}" pathLength="1" stroke-dasharray="1 1" fill="none" '
                f'stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>')

    for t, (task, route, caption) in zip(starts, TASKS):
        # the task slides toward the router
        slide = [(0.0, "opacity:0;transform:translateX(-14px)"), (t, "opacity:0;transform:translateX(-14px)"),
                 (t + 0.3, "opacity:1;transform:translateX(0)"), (t + 0.6, "opacity:1;transform:translateX(0)"),
                 (t + 0.95, "opacity:0;transform:translateX(40px)")]
        out.append(f'<g {an.attr(slide, base="opacity:0;")}>{chip(STAGE_X, ry, task, 11, p["track"], p)}</g>')

        color = p["hot"] if route == "queue" else p["cool_line"]
        if route == "orbit":
            out.append(beam((rx, ry - 17), (main_sat[0], main_sat[1] + 6), t + 0.9, color))
            out.append(beam((main_sat[0], main_sat[1] + 6), (station[0], station[1] - 20), t + 1.6, color))
        elif route == "gpu":
            out.append(beam((rx - 20, ry + 17), (gpu[0] + 6, gpu[1] - 20), t + 0.9, color))
        else:
            hold = window(t + 1.0, t + 2.6, 0.2)
            out.append(f'<text {an.attr(hold, base="opacity:0;", cls="small")} x="{rx}" y="{ry + 36}" text-anchor="middle" '
                       f'fill="{p["hot_text"]}">queued · next pass</text>')
        text_color = p["hot_text"] if route == "queue" else p["cool_text"]
        style = an.attr(window(t + 1.0, t + 2.9, 0.2), base="opacity:0;", cls="log")
        out.append(f'<text {style} x="{STAGE_X}" y="292"><tspan fill="{text_color}">{esc(caption)}</tspan></text>')
    return "".join(out)


# ---------------------------------------------------------------- backdrop and tile planet
# Style reference: the Semantic Router Labs launch video. A near-black sky with a burnt-orange
# nebula, small square "pixel" stars, and a planet built from square tiles that dissolve in and out.
TWINKLE_PERIODS = (3, 5, 6, 10)  # each divides CYCLE, so every star loops without a jump
SHOOTERS = [(60, 10, 4.0), (250, 18, 14.0), (140, 8, 24.0)]  # start x, start y, start time
PLANET = (596, 100, 32)  # center x, center y, radius
TILT = -18
TILE = 5


def lcg(seed: int):
    """A small deterministic random stream, so the artwork is the same on every build."""
    x = seed
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x / 0x7FFFFFFF


def ramp(v: float, stops: list) -> str:
    v = max(0.0, min(1.0, v))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if v <= b:
            f = (v - a) / (b - a)
            return "#%02x%02x%02x" % tuple(round(int(ca[i:i + 2], 16) * (1 - f) + int(cb[i:i + 2], 16) * f) for i in (1, 3, 5))
    return stops[-1][1]


def tile_cluster(x0: float, y0: float, cols: int, rows: int, size: float, seed: int, colors: list, fill_odds: float) -> str:
    """A loose block of faint tiles, like the corners of the video's end card."""
    rnd = lcg(seed)
    cells = []
    for gy in range(rows):
        for gx in range(cols):
            if next(rnd) < fill_odds * (1 - 0.6 * (gx + gy) / (cols + rows)):
                cells.append(f'<rect x="{x0 + gx * size:.0f}" y="{y0 + gy * size:.0f}" width="{size - 1}" height="{size - 1}" '
                             f'fill="{colors[int(next(rnd) * len(colors))]}"/>')
    return "".join(cells)


def space_defs(p: dict) -> str:
    glows = "".join(
        f'<radialGradient id="neb{i}" gradientUnits="userSpaceOnUse" cx="{x}" cy="{y}" r="{r}">'
        f'<stop offset="0" stop-color="{c}" stop-opacity="{o}"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for i, (x, y, r, c, o) in enumerate(p["glows"]))
    return (f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{p["bg"]}"/>'
            f'<stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>{glows}'
            f'<linearGradient id="streak" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity=".9"/></linearGradient>')


def backdrop(p: dict, an: Anims) -> str:
    """The dark sky (nebula, pixel stars, shooting stars) or the cream card (soft glow, tile clusters)."""
    out = [f'<rect width="1200" height="320" fill="url(#sky)"/>']
    out += [f'<rect width="1200" height="320" fill="url(#neb{i})"/>' for i in range(len(p["glows"]))]
    if p["mode"] == "light":
        out.append(f'<g opacity=".7">{tile_cluster(6, 6, 7, 5, 8, 3, ["#f2b98f", "#b9c8e8", "#e8a584"], 0.55)}'
                   f'{tile_cluster(1142, 262, 7, 7, 8, 5, ["#b9c8e8", "#f2b98f", "#9fd0cf"], 0.55)}</g>')
        return "".join(out)
    rnd = lcg(11)
    dots: dict[float, list[str]] = {0.35: [], 0.6: [], 0.9: []}
    twinkling = []
    for i in range(130):
        x, y, r, o = next(rnd) * 1200, 8 + next(rnd) * 304, 0.5 + next(rnd), next(rnd)
        if 40 < x < 600 and 76 < y < 212:  # keep the title area clear
            continue
        level = 0.35 if o < 0.5 else 0.6 if o < 0.85 else 0.9
        side = max(1.2, r * 1.6)
        if i % 9 == 0:
            twinkling.append((x, y, side, level))
        else:
            dots[level].append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{side:.1f}" height="{side:.1f}"/>')
    out += [f'<g fill="{p["text"]}" fill-opacity="{level}">{"".join(items)}</g>' for level, items in dots.items()]
    tints = (p["text"], p["amber"], p["cool"], p["text"])
    for k, (x, y, side, level) in enumerate(twinkling):
        period = TWINKLE_PERIODS[k % len(TWINKLE_PERIODS)]
        hi, lo = (level, level * 0.15) if k % 2 else (level * 0.15, level)
        frames = []
        for j in range(int(CYCLE // period)):
            frames += [(j * period, f"opacity:{hi:.2f}"), (j * period + period / 2, f"opacity:{lo:.2f}")]
        frames.append((CYCLE, f"opacity:{hi:.2f}"))
        out.append(f'<rect {an.attr(frames, base=f"opacity:{level};")} x="{x:.0f}" y="{y:.0f}" width="{side * 1.3:.1f}" '
                   f'height="{side * 1.3:.1f}" fill="{tints[k % 4]}"/>')
    for x, y, t in SHOOTERS:
        frames = [(0.0, "opacity:0;transform:translateX(0)"), (t, "opacity:0;transform:translateX(0)"),
                  (t + 0.05, "opacity:1;transform:translateX(0)"), (t + 0.85, "opacity:0;transform:translateX(230px)")]
        out.append(f'<g transform="translate({x} {y}) rotate(15)"><g {an.attr(frames, base="opacity:0;", timing="ease-in")}>'
                   f'<rect x="-80" y="-1" width="80" height="2" fill="url(#streak)"/><rect x="-2" y="-2" width="4" height="4" fill="#fff"/></g></g>')
    return "".join(out)


def planet(p: dict, an: Anims) -> str:
    """A planet and its ring built from square tiles. The tiles dissolve in at the start of each loop
    and out at the end, like the mosaic transitions in the video. A square moon passes behind and in front."""
    cx, cy, r = PLANET
    # six dissolve steps, each a group of tiles; the same six animations serve every layer
    steps = []
    for b in range(6):
        t_in, t_out = 0.1 + 0.15 * b, CYCLE - 1.3 + 0.15 * b
        steps.append(an.attr([(0.0, "opacity:0"), (t_in, "opacity:0"), (t_in + 0.25, "opacity:1"), (t_out, "opacity:1"), (t_out + 0.25, "opacity:0")],
                             base="opacity:1;", timing="steps(3)"))

    def layer(tiles: list[tuple[int, str]]) -> str:
        groups: list[list[str]] = [[] for _ in steps]
        for bucket, tile in tiles:
            groups[bucket].append(tile)
        return "".join(f'<g {steps[b]}>{"".join(g)}</g>' for b, g in enumerate(groups) if g)

    rnd = lcg(5)
    body = []
    for gy in range(-7, 8):
        for gx in range(-7, 8):
            nx, ny = gx * TILE / r, gy * TILE / r
            if nx * nx + ny * ny > 0.98:
                continue
            nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
            light = max(0.0, -0.5 * nx - 0.6 * ny + 0.62 * nz) + (next(rnd) - 0.5) * 0.14
            body.append((int(next(rnd) * 6), f'<rect x="{cx + gx * TILE - TILE / 2:.0f}" y="{cy + gy * TILE - TILE / 2:.0f}" '
                                              f'width="{TILE - 1}" height="{TILE - 1}" rx="1" fill="{ramp(light, p["ramp"])}"/>'))

    def ring_tiles(front: bool) -> list[tuple[int, str]]:
        tiles = []
        for rx, ry, row in ((60, 14, 0), (52, 12, 1)):
            for k in range(54):
                a = k / 54 * 2 * math.pi
                if (math.sin(a) > 0) != front:
                    continue
                x, y = rx * math.cos(a), ry * math.sin(a)
                c, s = math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
                px, py = round((cx + x * c - y * s) / 4) * 4, round((cy + x * s + y * c) / 4) * 4
                tiles.append((int(next(rnd) * 6), f'<rect x="{px - 2}" y="{py - 2}" width="3.4" height="3.4" fill="{p["ring"][(k + row) % len(p["ring"])]}" '
                                                  f'opacity="{0.95 if row == 0 else 0.6}"/>'))
        return tiles

    def moon(clip: str) -> str:
        orbit_rx, orbit_ry, n = 72, 20, 24
        frames = [(i * 10 / n, f"transform:translate({orbit_rx * math.cos(2 * math.pi * i / n):.1f}px,{orbit_ry * math.sin(2 * math.pi * i / n):.1f}px)")
                  for i in range(n + 1)]
        spin = an.attr(frames, timing="linear").replace('style="', 'style="animation-duration:10s;', 1)
        return (f'<g transform="rotate({TILT} {cx} {cy})"><g clip-path="url(#{clip})"><g transform="translate({cx} {cy})">'
                f'<rect {spin} x="-3.5" y="-3.5" width="7" height="7" fill="{p["text"]}"/></g></g></g>')

    defs = (f'<defs><radialGradient id="pglow" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="120"><stop offset="0" stop-color="#ff5b2b" stop-opacity="{p["pglow"]}"/>'
            f'<stop offset="1" stop-color="#ff5b2b" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="pback"><rect x="0" y="0" width="1200" height="{cy}"/></clipPath>'
            f'<clipPath id="pfront"><rect x="0" y="{cy}" width="1200" height="320"/></clipPath></defs>')
    return (defs + f'<circle cx="{cx}" cy="{cy}" r="120" fill="url(#pglow)"/>' + layer(ring_tiles(False)) + moon("pback")
            + layer(body) + layer(ring_tiles(True)) + moon("pfront"))


# ---------------------------------------------------------------- banner
def typed(command: str, start: float, p: dict, an: Anims) -> str:
    """A command line typed out from `start`, revealed one character at a time by a clip."""
    frames = [(0.0, "clip-path:inset(0 100% 0 0)"), (start, "clip-path:inset(0 100% 0 0)"), (start + 0.9, "clip-path:inset(0 0% 0 0)")]
    return f'<text {an.attr(frames, cls="mono", timing=f"steps({len(command)})")} x="66" y="262">{esc(command)}</text>'


def scene_header(title: str, subtitle: str, active: int, p: dict) -> str:
    """A small uppercase label led by an orange square, as in the video, and three scene squares."""
    squares = "".join(f'<rect x="{1150 + k * 12}" y="42" width="7" height="7" fill="{p["hot"] if k == active else p["track"]}"/>'
                      for k in range(3))
    return (f'<rect x="{STAGE_X}" y="42" width="7" height="7" fill="{p["hot"]}"/>'
            f'<text x="{STAGE_X + 15}" y="50" class="title">{esc(title)}<tspan class="subtitle"> · {esc(subtitle)}</tspan></text>{squares}')


def render(p: dict) -> str:
    an = Anims()
    a_style = an.attr(window(*SCENE_A, FADE), base="opacity:1;")
    b_style = an.attr(window(*SCENE_B, FADE), base="opacity:0;")
    c_style = an.attr(window(*SCENE_C, FADE), base="opacity:0;")
    a = (scene_header("META-RESEARCH", "AN AGENT OPTIMIZES A COLD PLATE", 0, p)
         + typed("$ meta-research run water_cooling", SCENE_A[0] + 0.2, p, an) + scene_a(p, an))
    b = (scene_header("vSR", "vLLM SEMANTIC ROUTER INSIDE CLAUDE CODE", 1, p)
         + typed("$ claude --plugin vsr", SCENE_B[0] + 0.2, p, an) + scene_b(p, an))
    c = (scene_header("ORBIT", "CONCEPT · ROUTING BEYOND THE DATA CENTER", 2, p)
         + typed("# what if routing reached orbit?", SCENE_C[0] + 0.2, p, an) + scene_c(p, an))
    sky = backdrop(p, an)
    world = planet(p, an)
    keyframes = "\n      ".join(an.rules)
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    sans = 'Manrope, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" width="1200" height="320" role="img" aria-labelledby="t d">
  <title id="t">Theo Hsiung</title>
  <desc id="d">AI for Science, LLM systems and agentic infrastructure, over {"a night sky with a warm nebula" if p["mode"] == "dark" else "a cream card with faint tile clusters"}, with a planet and a moon built from square tiles. Three alternating scenes: an agent optimizing a liquid-cooling cold plate, pushing the Pareto frontier of thermal resistance and pressure drop; vLLM Semantic Router inside Claude Code sending each prompt to the right model, masking a secret, and holding a risky Bash command; and a concept of routing compute to orbit, where raw imagery is processed on an orbital node, heavy training goes to ground GPUs, and a task with no ground link waits for the next pass.</desc>
  <!-- Generated by scripts/banner.py; edit the palette and scenes there, not here. -->
  <defs>
    <clipPath id="round"><rect width="1200" height="320" rx="16"/></clipPath>
    <linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{BAR[0]}"/><stop offset=".5" stop-color="{BAR[1]}"/><stop offset="1" stop-color="{BAR[2]}"/></linearGradient>
    <linearGradient id="tag" x1="0" x2="1"><stop offset="0" stop-color="{p["tag"][0]}"/><stop offset="1" stop-color="{p["tag"][1]}"/></linearGradient>
    <linearGradient id="nameg" x1="0" x2="1"><stop offset="0" stop-color="{p["name"][0]}"/><stop offset="1" stop-color="{p["name"][1]}"/></linearGradient>
    {space_defs(p)}
    <style>
      .name {{ font: 700 66px {sans}; fill: url(#nameg); letter-spacing: -2.6px; }}
      .tag {{ font: 600 22px {sans}; fill: url(#tag); letter-spacing: -.3px; }}
      .sub {{ font: 400 15px {sans}; fill: {p["muted"]}; }}
      .label {{ font: 600 10.5px {mono}; fill: {p["muted"]}; letter-spacing: 1.4px; }}
      .mono {{ font: 500 14px {mono}; fill: {p["muted"]}; }}
      .title {{ font: 700 10.5px {mono}; fill: {p["text"]}; letter-spacing: 1.3px; }}
      .subtitle {{ font-weight: 500; fill: {p["muted"]}; }}
      .small {{ font: 500 11px {mono}; fill: {p["muted"]}; }}
      .tiny {{ font: 500 10px {mono}; fill: {p["muted"]}; }}
      .log {{ font: 500 12px {mono}; fill: {p["muted"]}; }}
      .chip {{ font-family: {mono}; font-weight: 500; fill: {p["text"]}; }}
      .router {{ font: 700 14px {mono}; fill: {p["cool_text"]}; }}

      .a {{ animation-duration: {CYCLE:g}s; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
      .fb {{ transform-box: fill-box; transform-origin: center; }}
      .fl {{ transform-box: fill-box; transform-origin: left center; }}
      {keyframes}

      @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
    </style>
  </defs>

  <g clip-path="url(#round)">{sky}<rect width="1200" height="4" fill="url(#bar)"/></g>

  <rect x="66" y="52" width="8" height="8" fill="{p["hot"]}"/>
  <text x="82" y="60" class="label">BUILT IN THE OPEN · TAIWAN</text>
  <text x="64" y="124" class="name">Theo Hsiung</text>
  <text x="66" y="164" class="tag">AI for Science · LLM Systems · Agentic Infra</text>
  <text x="66" y="196" class="sub">Associate Research Scientist, vLLM Semantic Router · Delta Electronics · Taiwan</text>

  {world}

  <g {a_style}>{a}</g>
  <g {b_style}>{b}</g>
  <g {c_style}>{c}</g>
</svg>
'''


if __name__ == "__main__":
    assets = Path(__file__).resolve().parent.parent / "assets"
    for mode, palette in PALETTES.items():
        (assets / f"banner-{mode}.svg").write_text(render(palette), encoding="utf-8")
        print(f"wrote assets/banner-{mode}.svg")
