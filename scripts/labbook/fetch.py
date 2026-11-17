"""Read a user's merged pull requests from the GitHub search API."""

import json
import urllib.parse
import urllib.request

API = "https://api.github.com/search/issues"
PER_PAGE = 100


def search_url(user: str, page: int) -> str:
    query = urllib.parse.quote(f"author:{user} is:pr is:merged")
    return f"{API}?q={query}&sort=updated&order=desc&per_page={PER_PAGE}&page={page}"


def headers(token: str | None) -> dict[str, str]:
    out = {"Accept": "application/vnd.github+json", "User-Agent": "labbook"}
    if token:
        out["Authorization"] = f"Bearer {token}"
    return out


def fetch_items(user: str, token: str | None = None, opener=urllib.request.urlopen) -> list[dict]:
    request = urllib.request.Request(search_url(user, 1), headers=headers(token))
    with opener(request, timeout=30) as response:
        return json.load(response).get("items", [])
