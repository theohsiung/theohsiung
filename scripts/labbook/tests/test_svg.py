import unittest

from svg import el, esc


class SvgTest(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(esc('<a & "b">'), "&lt;a &amp; &quot;b&quot;&gt;")

    def test_attribute_names(self):
        self.assertEqual(el("text", "hi", class_="x", text_anchor="end"), '<text class="x" text-anchor="end">hi</text>')

    def test_empty_body_self_closes_and_none_is_dropped(self):
        self.assertEqual(el("rect", width=2, fill=None), '<rect width="2"/>')


if __name__ == "__main__":
    unittest.main()
