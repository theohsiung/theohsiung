import unittest

from anim import CYCLE, Anims, appear


class AnimTest(unittest.TestCase):
    def test_keyframes_span_the_whole_cycle(self):
        anims = Anims()
        anims.attr([(2.0, "opacity:1")], base="opacity:1;")
        rule = anims.rules[0]
        self.assertIn("0.000% { opacity:1 }", rule)
        self.assertIn("100.000% { opacity:1 }", rule)

    def test_attr_keeps_a_static_style_for_reduced_motion(self):
        attr = Anims().attr(appear(1.0), base="opacity:1;", cls="grow")
        self.assertIn('class="a grow"', attr)
        self.assertIn("opacity:1;animation-name:k0;", attr)

    def test_appear_hides_before_the_loop_restarts(self):
        frames = appear(1.0)
        self.assertEqual(frames[0][1], "opacity:0")
        self.assertEqual(frames[-1][1], "opacity:0")
        self.assertLess(frames[-1][0], CYCLE)


if __name__ == "__main__":
    unittest.main()
