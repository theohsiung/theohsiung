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


def heart_path(x: float, y: float, size: float) -> str:
    """Path data for a heart centered on (x, y), `size` wide."""
    s = size / 2
    return (f"M{x} {y + s * 0.9} C{x - s * 1.4} {y - s * 0.1} {x - s * 0.6} {y - s * 1.1} {x} {y - s * 0.35} "
            f"C{x + s * 0.6} {y - s * 1.1} {x + s * 1.4} {y - s * 0.1} {x} {y + s * 0.9} Z")
