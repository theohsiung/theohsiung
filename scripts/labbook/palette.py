"""Colors for the lab notebook card, taken from scripts/banner.py."""

PALETTES = {
    "dark": {
        "bg": "#0d1117", "panel": "#161b22", "grid": "#1c2129", "track": "#30363d",
        "text": "#e6edf3", "muted": "#7d8590", "accent": "#e8577a", "blue": "#a6cdec",
    },
    "light": {
        "bg": "#ffffff", "panel": "#f6f8fa", "grid": "#e4e7eb", "track": "#d0d7de",
        "text": "#1f2328", "muted": "#6e7781", "accent": "#881337", "blue": "#4a78a6",
    },
}

# One color per area, from wine to powder blue. Both themes share them.
AREA_COLORS = {
    "runtime": "#881337",
    "security": "#be123c",
    "harness": "#c9405f",
    "perf": "#a78bb5",
    "protocol": "#a6cdec",
    "other": "#57606a",
}
