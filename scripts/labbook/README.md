# labbook

Draws the lab notebook card on the profile README: the newest merged pull
requests on the left, typed in one line at a time, and merged pull requests
per week by area of work on the right.

```bash
python3 scripts/labbook --out dist                                          # live, from GitHub
python3 scripts/labbook --fixture scripts/labbook/tests/fixtures/search.json  # offline
PYTHONPATH=scripts/labbook python3 -m unittest discover -s scripts/labbook/tests
```

It uses only the standard library. Set `GITHUB_TOKEN` to avoid the search
API's anonymous rate limit. Pull requests to the profile repo itself are left
out by default; pass `--exclude OWNER/REPO` to choose others.

The `labbook` workflow runs it daily and publishes `labbook-dark.svg` and
`labbook-light.svg` to the `labbook` branch.

| File | Owns |
|---|---|
| `fetch.py`, `parse.py` | GitHub search results to `Entry` records |
| `areas.py` | the keyword rules that pick an area from a title |
| `weeks.py` | per-week counts |
| `header.py`, `log.py`, `chart.py`, `legend.py`, `footer.py` | one part of the card each |
| `card.py`, `layout.py`, `palette.py`, `anim.py` | assembly, positions, colors, animation clock |
| `cli.py` | arguments and file output |
