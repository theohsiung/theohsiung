"""Read a user's merged pull requests from the GitHub search API."""

import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

API = "https://api.github.com/search/issues"
PER_PAGE = 100
MAX_PAGES = 10  # the search API stops at 1000 results


class FetchError(RuntimeError):
    pass


def search_url(user: str, page: int) -> str:
    query = urllib.parse.quote(f"author:{user} is:pr is:merged")
    return f"{API}?q={query}&sort=updated&order=desc&per_page={PER_PAGE}&page={page}"


def headers(token: str | None) -> dict[str, str]:
    out = {"Accept": "application/vnd.github+json", "User-Agent": "labbook"}
    if token:
        out["Authorization"] = f"Bearer {token}"
    return out


def fetch_items(user: str, token: str | None = None, opener=urllib.request.urlopen) -> list[dict]:
    items: list[dict] = []
    for page in range(1, MAX_PAGES + 1):
        request = urllib.request.Request(search_url(user, page), headers=headers(token))
        try:
            with opener(request, timeout=30) as response:
                batch = json.load(response).get("items", [])
        except HTTPError as err:
            hint = " (rate limited; set GITHUB_TOKEN)" if err.code in (403, 429) else ""
            raise FetchError(f"GitHub search returned HTTP {err.code}{hint}") from err
        except URLError as err:
            raise FetchError(f"could not reach GitHub: {err.reason}") from err
        items.extend(batch)
        if len(batch) < PER_PAGE:
            break
    return items
