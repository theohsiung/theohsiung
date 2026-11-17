import unittest

from fetch import headers, search_url


class FetchTest(unittest.TestCase):
    def test_search_url(self):
        url = search_url("theohsiung", 2)
        self.assertIn("q=author%3Atheohsiung%20is%3Apr%20is%3Amerged", url)
        self.assertTrue(url.endswith("&page=2"))

    def test_token_is_optional(self):
        self.assertNotIn("Authorization", headers(None))
        self.assertEqual(headers("abc")["Authorization"], "Bearer abc")


if __name__ == "__main__":
    unittest.main()
