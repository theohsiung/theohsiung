import unittest
import xml.etree.ElementTree as ET

from card import render_card
from helpers import NOW, items
from layout import LOG_ROWS
from palette import PALETTES
from parse import parse_items

NS = "{http://www.w3.org/2000/svg}"


class CardTest(unittest.TestCase):
    def setUp(self):
        self.entries = parse_items(items(), exclude=("theohsiung/theohsiung",))

    def render(self, entries, theme="dark"):
        return ET.fromstring(render_card(entries, "theohsiung", NOW, PALETTES[theme]))

    def test_both_themes_are_valid_svg(self):
        for theme in PALETTES:
            with self.subTest(theme=theme):
                self.assertEqual(self.render(self.entries, theme).tag, f"{NS}svg")

    def test_shows_the_newest_rows_only(self):
        text = render_card(self.entries, "theohsiung", NOW, PALETTES["dark"])
        self.assertIn("semantic-router#6113", text)
        self.assertEqual(text.count('class="ref"') // 2, LOG_ROWS)

    def test_reduced_motion_stops_animation(self):
        text = render_card(self.entries, "theohsiung", NOW, PALETTES["dark"])
        self.assertIn("prefers-reduced-motion", text)

    def test_empty_history(self):
        text = render_card([], "theohsiung", NOW, PALETTES["light"])
        self.assertIn("no merged pull requests yet", text)
        ET.fromstring(text)


if __name__ == "__main__":
    unittest.main()
