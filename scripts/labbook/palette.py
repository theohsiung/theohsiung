"""Colors for the lab notebook card, taken from scripts/banner.py."""

PALETTES = {
    "dark": {
        "bg": "#19381f", "panel": "#1f4227", "grid": "#21472a", "track": "#2f5a36",
        "text": "#f7f6d8", "muted": "#a9c39a", "accent": "#eee82c", "blue": "#91cb3e",
    },
    "light": {
        "bg": "#f8faf0", "panel": "#eef5e2", "grid": "#e7efd8", "track": "#cfe0b8",
        "text": "#19381f", "muted": "#4c934c", "accent": "#53a548", "blue": "#4c934c",
    },
}

# One color per area, from lemon to forest green. Both themes share them.
AREA_COLORS = {
    "runtime": "#eee82c",
    "security": "#d6e681",
    "harness": "#91cb3e",
    "routing": "#53a548",
    "perf": "#c5e38f",
    "protocol": "#7fb069",
    "research": "#4c934c",
    "upkeep": "#a3c585",
    "other": "#8aa58a",
}
