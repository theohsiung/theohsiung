import unittest

from svg import el, esc, star_path


class SvgTest(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(esc('<a & "b">'), "&lt;a &amp; &quot;b&quot;&gt;")

    def test_attribute_names(self):
        self.assertEqual(el("text", "hi", class_="x", text_anchor="end"), '<text class="x" text-anchor="end">hi</text>')

    def test_empty_body_self_closes_and_none_is_dropped(self):
        self.assertEqual(el("rect", width=2, fill=None), '<rect width="2"/>')

    def test_star_is_a_closed_path_with_a_point_straight_above_its_center(self):
        d = star_path(10, 20, 8)
        self.assertTrue(d.startswith("M10 16.0 ") and d.endswith(" Z"))


if __name__ == "__main__":
    unittest.main()
