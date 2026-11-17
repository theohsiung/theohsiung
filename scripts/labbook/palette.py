"""Colors for the lab notebook card, taken from scripts/banner.py."""

PALETTES = {
    "dark": {
        "bg": "#1f1a2e", "panel": "#2a2340", "grid": "#2e2740", "track": "#4a3f63",
        "text": "#fdf2f8", "muted": "#b8a9cf", "accent": "#f9a8d4", "blue": "#a5d8ff",
    },
    "light": {
        "bg": "#fff7fb", "panel": "#fdf2f8", "grid": "#fce7f3", "track": "#f5d0e6",
        "text": "#5b3a6b", "muted": "#a58bb3", "accent": "#ec4899", "blue": "#7c9ef0",
    },
}

# One pastel per area. Both themes share them.
AREA_COLORS = {
    "runtime": "#f472b6",
    "security": "#fb7185",
    "harness": "#c084fc",
    "routing": "#f9a8d4",
    "perf": "#fcd34d",
    "protocol": "#93c5fd",
    "research": "#6ee7b7",
    "upkeep": "#c4b5fd",
    "other": "#b8a9cf",
}
