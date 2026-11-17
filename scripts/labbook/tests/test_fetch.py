import io
import json
import unittest
from urllib.error import HTTPError

from fetch import PER_PAGE, FetchError, fetch_items, headers, search_url


def fake_opener(pages):
    calls = []

    def opener(request, timeout):
        calls.append(request.full_url)
        return io.BytesIO(json.dumps({"items": pages[len(calls) - 1]}).encode())

    return opener, calls


class FetchTest(unittest.TestCase):
    def test_search_url(self):
        url = search_url("theohsiung", 2)
        self.assertIn("q=author%3Atheohsiung%20is%3Apr%20is%3Amerged", url)
        self.assertTrue(url.endswith("&page=2"))

    def test_token_is_optional(self):
        self.assertNotIn("Authorization", headers(None))
        self.assertEqual(headers("abc")["Authorization"], "Bearer abc")

    def test_stops_after_a_short_page(self):
        opener, calls = fake_opener([[{}] * PER_PAGE, [{}] * 3])
        self.assertEqual(len(fetch_items("u", opener=opener)), PER_PAGE + 3)
        self.assertEqual(len(calls), 2)

    def test_rate_limit_names_the_fix(self):
        def opener(request, timeout):
            raise HTTPError(request.full_url, 403, "Forbidden", {}, None)

        with self.assertRaisesRegex(FetchError, "GITHUB_TOKEN"):
            fetch_items("u", opener=opener)


if __name__ == "__main__":
    unittest.main()
