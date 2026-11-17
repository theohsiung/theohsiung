"""Sort a pull request into an area of work by keywords in its title.

The first rule that matches wins, so the more specific areas come first and
`routing`, which catches most remaining router work, comes last.
"""

AREAS = ("runtime", "security", "harness", "routing", "perf", "protocol", "research", "upkeep", "other")

RULES = (
    ("security", ("jailbreak", "security", "leak", "injection", "pii", "fail-closed", "risk_score")),
    ("runtime", ("model runtime", "nvfp4", "fp4", "vela", "rocm", "kernel", "quant", "bindings", "bert", "cuda")),
    ("harness", ("claude code", "plugin", "skill", "harness", "vsr", "agent")),
    ("perf", ("bench", "perf", "latency", "alloc", "regression", "dedup", "bound the")),
    ("protocol", ("looper", "header", "protocol", "sse", "stream", "response", "codec", "chat completions")),
    ("research", ("[research]", "hypothes", "ledger", "whitepaper", "knowledge graph", "thinking")),
    ("upkeep", ("[docs]", "docs:", "[website]", "[community]", "[test]", "e2e", " test", "leaderboard")),
    ("routing", ("[router]", "routing", "route", "decision", "signal", "cache", "session", "classify", "model")),
)


def classify(title: str) -> str:
    text = title.lower()
    for area, words in RULES:
        if any(word in text for word in words):
            return area
    return "other"
