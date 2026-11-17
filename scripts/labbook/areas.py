"""Sort a pull request into an area of work by keywords in its title.

The areas match the Open source table in README.md. The first rule that
matches wins, so put the more specific areas first.
"""

AREAS = ("runtime", "security", "harness", "perf", "protocol", "other")

RULES = (
    ("security", ("jailbreak", "security", "leak", "injection", "pii", "fail-closed", "risk_score")),
    ("runtime", ("model runtime", "nvfp4", "fp4", "vela", "rocm", "kernel", "quant", "bindings", "bert", "cuda")),
    ("harness", ("claude code", "plugin", "skill", "harness", "vsr", "agent")),
    ("perf", ("bench", "perf", "latency", "alloc", "regression", "dedup", "bound the")),
    ("protocol", ("looper", "header", "protocol", "sse", "stream", "response", "codec", "chat completions")),
)


def classify(title: str) -> str:
    text = title.lower()
    for area, words in RULES:
        if any(word in text for word in words):
            return area
    return "other"
