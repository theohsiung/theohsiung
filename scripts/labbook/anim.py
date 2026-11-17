"""CSS keyframes on one shared clock, in the style of scripts/banner.py.

Every animated element also gets a static style, which is what viewers with
prefers-reduced-motion see.
"""

CYCLE = 12.0


class Anims:
    def __init__(self) -> None:
        self.rules: list[str] = []

    def attr(self, frames: list[tuple[float, str]], base: str, cls: str = "") -> str:
        frames = sorted(frames)
        if frames[0][0] > 0:
            frames.insert(0, (0.0, frames[0][1]))
        if frames[-1][0] < CYCLE:
            frames.append((CYCLE, frames[-1][1]))
        name = f"k{len(self.rules)}"
        body = " ".join(f"{min(t, CYCLE) / CYCLE * 100:.3f}% {{ {css} }}" for t, css in frames)
        self.rules.append(f"@keyframes {name} {{ {body} }}")
        classes = " ".join(c for c in ("a", cls) if c)
        return f'class="{classes}" style="{base}animation-name:{name};"'


def appear(start: float, end: float = CYCLE - 0.8, fade: float = 0.35, hidden: str = "opacity:0",
           shown: str = "opacity:1") -> list[tuple[float, str]]:
    """Hidden until `start`, shown until `end`, hidden again before the cycle restarts."""
    return [(0.0, hidden), (start, hidden), (start + fade, shown), (end, shown), (end + fade, hidden)]
