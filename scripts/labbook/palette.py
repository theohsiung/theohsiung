"""Colors for the lab notebook card. They match scripts/banner.py, which samples the Semantic Router Labs launch video."""

PALETTES = {
    "dark": {
        "bg": "#05080e", "panel": "#0c1119", "grid": "#141824", "track": "#2b2e3a",
        "text": "#f2efe9", "muted": "#9b9aa3", "accent": "#ff5b2b", "blue": "#97dbd9",
    },
    "light": {
        "bg": "#e8e6e3", "panel": "#f4f2ed", "grid": "#dcd9d1", "track": "#c9c6bd",
        "text": "#14151a", "muted": "#66655f", "accent": "#d63a15", "blue": "#3f9a98",
    },
}

# One color per area, from orange through amber and peach to teal and periwinkle. Both themes share them.
AREA_COLORS = {
    "runtime": "#ff5b2b",
    "security": "#ffd183",
    "harness": "#869bdc",
    "routing": "#f4a77a",
    "perf": "#97dbd9",
    "protocol": "#b9b4e8",
    "research": "#6f9bc9",
    "upkeep": "#a39f94",
    "other": "#7a776f",
}
