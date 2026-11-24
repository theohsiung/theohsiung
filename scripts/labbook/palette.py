"""Colors for the lab notebook card. The space palette matches scripts/banner.py."""

PALETTES = {
    "dark": {
        "bg": "#060814", "panel": "#0d1330", "grid": "#151c44", "track": "#26306a",
        "text": "#eaf1ff", "muted": "#8f9dc9", "accent": "#5ee7ff", "blue": "#8b6cff",
    },
    "light": {
        "bg": "#f5f7ff", "panel": "#e9edff", "grid": "#dfe4fb", "track": "#c3cbf0",
        "text": "#0b1030", "muted": "#4c5a94", "accent": "#0891b2", "blue": "#5b3fe0",
    },
}

# One color per area, from amber through pink and violet to cyan. Both themes share them.
AREA_COLORS = {
    "runtime": "#ffb454",
    "security": "#ff5fb0",
    "harness": "#8b6cff",
    "routing": "#38bdf8",
    "perf": "#22d3ee",
    "protocol": "#a78bfa",
    "research": "#3b82f6",
    "upkeep": "#94a3d8",
    "other": "#6b7aa8",
}
