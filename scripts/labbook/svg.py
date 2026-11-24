"""Small helpers for writing SVG by hand."""


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def el(tag: str, body: str = "", **attrs) -> str:
    """`class_` becomes class and `font_size` becomes font-size. None values are dropped."""
    parts = [tag]
    for key, value in attrs.items():
        if value is None:
            continue
        name = key.rstrip("_").replace("_", "-")
        parts.append(f'{name}="{esc(str(value))}"')
    head = " ".join(parts)
    return f"<{head}>{body}</{tag}>" if body else f"<{head}/>"



def star_path(x: float, y: float, size: float) -> str:
    """Path data for a four-pointed star centered on (x, y), `size` across."""
    s, k = size / 2, size * 0.14
    return (f"M{x} {y - s} Q{x + k} {y - k} {x + s} {y} Q{x + k} {y + k} {x} {y + s} "
            f"Q{x - k} {y + k} {x - s} {y} Q{x - k} {y - k} {x} {y - s} Z")
