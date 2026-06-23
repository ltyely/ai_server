#!/usr/bin/env python3
"""解析 llama-server log，提取性能与稳定性指标。"""
import re
import sys
from pathlib import Path
from collections import defaultdict

PATTERNS = {
    "prompt_eval_time": re.compile(r"prompt eval time\s*=\s*([\d.]+)\s*ms\s*/\s*([\d]+)\s*tokens.*?([\d.]+)\s*tokens per second"),
    "eval_time": re.compile(r"eval time\s*=\s*([\d.]+)\s*ms\s*/\s*([\d]+)\s*tokens.*?([\d.]+)\s*tokens per second"),
    "tg_speed": re.compile(r"n_decoded\s*=\s*\d+,\s*tg\s*=\s*([\d.]+)\s*t/s"),
    "draft_acceptance": re.compile(r"draft acceptance\s*=\s*([\d.]+)\s*\(\s*(\d+)\s*accepted\s*/\s*(\d+)\s*generated\).*?mean acceptance length\s*=\s*([\d.]+)"),
    "accept_rate_pos": re.compile(r"acceptance rate per position\s*=\s*\(([\d.,\s]+)\)"),
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

    for match in PATTERNS["prompt_eval_time"].finditer(text):
        stats["prompt_eval_ms"].append(float(match.group(1)))
        stats["prompt_eval_tokens"].append(int(match.group(2)))
        stats["prompt_eval_tps"].append(float(match.group(3)))

    for match in PATTERNS["eval_time"].finditer(text):
        stats["eval_ms"].append(float(match.group(1)))
        stats["eval_tokens"].append(int(match.group(2)))
        stats["eval_tps"].append(float(match.group(3)))

    for match in PATTERNS["tg_speed"].finditer(text):
        stats["tg_tps"].append(float(match.group(1)))

    for match in PATTERNS["draft_acceptance"].finditer(text):
        stats["draft_acceptance_ratio"].append(float(match.group(1)))
        stats["draft_accepted"].append(int(match.group(2)))
        stats["draft_generated"].append(int(match.group(3)))
        stats["draft_mean_length"].append(float(match.group(4)))

    for match in PATTERNS["accept_rate_pos"].finditer(text):
        parts = [float(x.strip()) for x in match.group(1).split(",")]
        stats["accept_rate_per_position"].append(parts)

    return stats, flags


def summarize(values):
    if not values:
        return None
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0],
    }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <server-log-file>")
        sys.exit(1)
    path = sys.argv[1]
    stats, flags = parse_log(path)

    print(f"# Server log summary: {path}")
    print()

    sections = [
        ("TTFT / Prompt eval time (ms)", "prompt_eval_ms"),
        ("Prompt eval tokens", "prompt_eval_tokens"),
        ("Prompt eval speed (tokens/s)", "prompt_eval_tps"),
        ("Generation eval time (ms)", "eval_ms"),
        ("Generation eval tokens", "eval_tokens"),
        ("Generation eval speed (tokens/s)", "eval_tps"),
        ("TG speed (t/s)", "tg_tps"),
        ("MTP draft acceptance ratio", "draft_acceptance_ratio"),
        ("MTP draft accepted count", "draft_accepted"),
        ("MTP draft generated count", "draft_generated"),
        ("MTP mean acceptance length", "draft_mean_length"),
    ]

    for title, key in sections:
        s = summarize(stats[key])
        if s:
            print(f"## {title}")
            print(f"- count: {s['count']}")
            print(f"- mean: {s['mean']:.2f}")
            print(f"- min: {s['min']:.2f}")
            print(f"- max: {s['max']:.2f}")
            print(f"- p95: {s['p95']:.2f}")
            print()

    if stats["accept_rate_per_position"]:
        # 按位置平均
        max_len = max(len(x) for x in stats["accept_rate_per_position"])
        pos_means = []
        for i in range(max_len):
            vals = [x[i] for x in stats["accept_rate_per_position"] if i < len(x)]
            pos_means.append(sum(vals) / len(vals) if vals else 0)
        print("## MTP acceptance rate per position")
        for i, v in enumerate(pos_means):
            print(f"- position {i}: {v:.3f}")
        print()

    print("## Stability flags")
    for key, value in flags.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()
