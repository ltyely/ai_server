#!/usr/bin/env python3
"""汇总各项 benchmark 结果生成 baseline-report.md。"""
import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def load_json(path: str):
    if not path or not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def summarize(values):
    if not values:
        return None
    sorted_vals = sorted(values)
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
        "p95": sorted_vals[int(len(values) * 0.95)] if len(values) > 1 else values[0],
    }


def parse_log(log_path: str):
    if not log_path or not Path(log_path).exists():
        return {}, {}
    text = Path(log_path).read_text(encoding="utf-8", errors="ignore")
    stats = defaultdict(list)

    # prompt eval: time ms / tokens (ms per token, tokens/s)
    for m in re.finditer(r"prompt eval time\s*=\s*([\d.]+)\s*ms\s*/\s*([\d]+)\s*tokens.*?([\d.]+)\s*tokens per second", text):
        stats["ttft_ms"].append(float(m.group(1)))
        stats["prompt_tokens"].append(int(m.group(2)))
        stats["prompt_tps"].append(float(m.group(3)))

    # generation eval: time ms / tokens (ms per token, tokens/s)
    for m in re.finditer(r"\s+eval time\s*=\s*([\d.]+)\s*ms\s*/\s*([\d]+)\s*tokens.*?([\d.]+)\s*tokens per second", text):
        stats["gen_time_ms"].append(float(m.group(1)))
        stats["gen_tokens"].append(int(m.group(2)))
        stats["gen_tps"].append(float(m.group(3)))

    # TG speed
    for m in re.finditer(r"n_decoded\s*=\s*\d+,\s*tg\s*=\s*([\d.]+)\s*t/s", text):
        stats["tg_tps"].append(float(m.group(1)))

    # MTP draft acceptance
    for m in re.finditer(r"draft acceptance\s*=\s*([\d.]+)\s*\(\s*(\d+)\s*accepted\s*/\s*(\d+)\s*generated\).*?mean acceptance length\s*=\s*([\d.]+)", text):
        stats["mtp_acceptance_ratio"].append(float(m.group(1)))
        stats["mtp_accepted"].append(int(m.group(2)))
        stats["mtp_generated"].append(int(m.group(3)))
        stats["mtp_mean_length"].append(float(m.group(4)))

    # Acceptance rate per position
    for m in re.finditer(r"acceptance rate per position\s*=\s*\(([\d.,\s]+)\)", text):
        parts = [float(x.strip()) for x in m.group(1).split(",")]
        stats["mtp_accept_rate_per_position"].append(parts)

    flags = {
        "full_reprocess_count": len(re.findall(r"forcing full prompt re-processing", text)),
        "lack_cache_count": len(re.findall(r"lack of cache data", text)),
        "oom_count": len(re.findall(r"out of memory|OOM|failed to allocate", text, re.IGNORECASE)),
    }
    return stats, flags


def format_summary(s):
    if not s:
        return "N/A"
    return f"count={s['count']}, mean={s['mean']:.2f}, min={s['min']:.2f}, max={s['max']:.2f}, p95={s['p95']:.2f}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--short")
    parser.add_argument("--json")
    parser.add_argument("--context")
    parser.add_argument("--long-session")
    parser.add_argument("--log")
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/baseline-report.md")
    args = parser.parse_args()

    short = load_json(args.short)
    json_test = load_json(args.json)
    context = load_json(args.context)
    long_session = load_json(args.long_session)
    log_stats, log_flags = parse_log(args.log) if args.log else ({}, {})

    lines = [
        "# 基线测试报告",
        "",
        f"生成时间：{datetime.now().isoformat()}",
        "",
        "## 测试环境",
        "",
        "- GPU: Radeon RX 7900 XTX (gfx1100)",
        "- VRAM: 24560 MB",
        "- ROCm: 7.2.2 (当前环境未安装 7.14 / TheRock)",
        "- llama.cpp commit: 721354fbdfb7743e2be2183d918a3cdb9276c70f",
        "- Model: qwen36-27b-daily-mtp-65k",
        "",
        "## 关键性能指标（来自 server log）",
        "",
    ]

    ttft = summarize(log_stats.get("ttft_ms", []))
    prompt_tps = summarize(log_stats.get("prompt_tps", []))
    gen_tps = summarize(log_stats.get("gen_tps", []))
    tg_tps = summarize(log_stats.get("tg_tps", []))
    mtp_ratio = summarize(log_stats.get("mtp_acceptance_ratio", []))
    mtp_length = summarize(log_stats.get("mtp_mean_length", []))

    lines.extend([
        f"- **首 token 加载时间 / Prompt eval time (TTFT, ms)**: {format_summary(ttft)}",
        f"- **Prompt eval 速度 (tokens/s)**: {format_summary(prompt_tps)}",
        f"- **Generation eval 速度 (tokens/s)**: {format_summary(gen_tps)}",
        f"- **TG speed (tokens/s)**: {format_summary(tg_tps)}",
        f"- **MTP 投机解码命中率 (acceptance ratio)**: {format_summary(mtp_ratio)}",
        f"- **MTP 平均接受长度 (mean acceptance length)**: {format_summary(mtp_length)}",
    ])

    if log_stats.get("mtp_accept_rate_per_position"):
        max_len = max(len(x) for x in log_stats["mtp_accept_rate_per_position"])
        pos_means = []
        for i in range(max_len):
            vals = [x[i] for x in log_stats["mtp_accept_rate_per_position"] if i < len(x)]
            pos_means.append(sum(vals) / len(vals) if vals else 0)
        lines.append("- **MTP 各位置命中率**:")
        for i, v in enumerate(pos_means):
            lines.append(f"  - position {i}: {v:.3f}")

    lines.append("")

    lines.append("## 短请求测试 (100 次)")
    lines.append("")
    if short:
        s = short["summary"]
        lines.extend([
            f"- 成功率：{s['success']}/{s['count']}",
            f"- 平均延迟：{s['mean_latency']:.3f}s",
            f"- P95 延迟：{s['p95_latency']:.3f}s",
            f"- 最小/最大延迟：{s['min_latency']:.3f}s / {s['max_latency']:.3f}s",
            f"- 总生成 tokens：{s['total_completion_tokens']}",
        ])
    else:
        lines.append("- 未执行")
    lines.append("")

    lines.append("## JSON / 工具调用稳定性测试 (50 次)")
    lines.append("")
    if json_test:
        s = json_test["summary"]
        lines.extend([
            f"- 成功请求：{s['success']}/{s['count']}",
            f"- JSON 可解析：{s['valid_json']}/{s['count']}",
            f"- JSON 解析率：{s['valid_rate']*100:.1f}%",
        ])
    else:
        lines.append("- 未执行")
    lines.append("")

    lines.append("## 中长上下文测试")
    lines.append("")
    if context:
        for ctx, s in context["summary"].items():
            lines.append(f"- {ctx} tokens: 成功 {s['success']}/3, 平均耗时 {s['mean_elapsed']:.2f}s, 平均 prompt tokens {s['mean_prompt_tokens']}")
    else:
        lines.append("- 未执行")
    lines.append("")

    lines.append("## 长会话 Agent 模拟")
    lines.append("")
    if long_session:
        s = long_session["summary"]
        lines.extend([
            f"- 总轮数：{s['rounds']}",
            f"- 成功轮数：{s['successful_rounds']}",
            f"- 最终累计 tokens：{s['final_total_tokens']}",
            f"- 平均单轮耗时：{s['mean_elapsed']:.2f}s",
            f"- 最大单轮耗时：{s['max_elapsed']:.2f}s",
        ])
    else:
        lines.append("- 未执行")
    lines.append("")

    lines.append("## Server log 稳定性标记")
    lines.append("")
    for k, v in log_flags.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## 结论")
    lines.append("")
    if json_test and json_test["summary"]["valid_rate"] >= 0.95:
        lines.append("- JSON 解析率 >= 95%，通过最低验收。")
    elif json_test:
        lines.append("- JSON 解析率 < 95%，未通过最低验收，需进一步调优 sampling 参数。")
    else:
        lines.append("- JSON 测试未执行。")
    if ttft and ttft["max"] > 120000:
        lines.append("- 60K 上下文 TTFT 超过 120s，需关注 context size 或 batch 调优。")
    elif ttft:
        lines.append("- 60K 上下文 TTFT 在可接受范围内。")
    lines.append("")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
