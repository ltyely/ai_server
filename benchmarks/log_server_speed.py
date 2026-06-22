#!/usr/bin/env python3
"""解析 llama-server log，提取性能指标。"""
import re
import sys
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    "prompt_eval_time": re.compile(r"prompt eval time\s*=\s*([\d.]+)\s*ms"),
    "prompt_eval_rate": re.compile(r"prompt eval rate\s*=\s*([\d.]+)\s*tokens/sec"),
    "eval_time": re.compile(r"eval time\s*=\s*([\d.]+)\s*ms"),
    "eval_rate": re.compile(r"eval rate\s*=\s*([\d.]+)\s*tokens/sec"),
    "mtp_accepted": re.compile(r"MTP accepted tokens:\s*(\d+)"),
    "mtp_acceptance_rate": re.compile(r"MTP acceptance rate:\s*([\d.]+)%"),
    "full_reprocess": re.compile(r"forcing full prompt re-processing"),
    "lack_cache": re.compile(r"lack of cache data"),
    "oom": re.compile(r"out of memory|OOM|failed to allocate", re.IGNORECASE),
}


def parse_log(path: str):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    stats = defaultdict(list)
    flags = {
        "full_reprocess_count": len(PATTERNS["full_reprocess"].findall(text)),
        "lack_cache_count": len(PATTERNS["lack_cache"].findall(text)),
        "oom_count": len(PATTERNS["oom"].findall(text)),
    }
    for key, pattern in PATTERNS.items():
        if key in ("full_reprocess", "lack_cache", "oom"):
            continue
        for match in pattern.finditer(text):
            stats[key].append(float(match.group(1)))
    return stats, flags


def summarize(values):
    if not values:
        return None
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <server-log-file>")
        sys.exit(1)
    path = sys.argv[1]
    stats, flags = parse_log(path)
    print(f"# Server log summary: {path}")
    print()
    for key, values in stats.items():
        s = summarize(values)
        if s:
            print(f"- {key}: count={s['count']}, mean={s['mean']:.2f}, min={s['min']:.2f}, max={s['max']:.2f}")
    print()
    print("# Stability flags")
    for key, value in flags.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
