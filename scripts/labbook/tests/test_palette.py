import re
import unittest

from areas import AREAS
from palette import AREA_COLORS, PALETTES


class PaletteTest(unittest.TestCase):
    def test_themes_share_keys(self):
        self.assertEqual(PALETTES["dark"].keys(), PALETTES["light"].keys())

    def test_every_area_has_a_color(self):
        self.assertEqual(set(AREA_COLORS), set(AREAS))

    def test_colors_are_hex(self):
        colors = list(AREA_COLORS.values()) + [c for p in PALETTES.values() for c in p.values()]
        for color in colors:
            self.assertRegex(color, re.compile(r"^#[0-9a-f]{6}$"))


if __name__ == "__main__":
    unittest.main()
