import unittest

from svg import esc


class SvgTest(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(esc('<a & "b">'), "&lt;a &amp; &quot;b&quot;&gt;")


if __name__ == "__main__":
    unittest.main()
