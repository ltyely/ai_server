#!/usr/bin/env python3
"""汇总各项 benchmark 结果生成 baseline-report.md。"""
import argparse
import json
from pathlib import Path
from datetime import datetime


def load_json(path: str):
    if not path or not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def parse_log(log_path: str):
    if not log_path or not Path(log_path).exists():
        return {}
    import re
    text = Path(log_path).read_text(encoding="utf-8", errors="ignore")
    return {
        "full_reprocess": len(re.findall(r"forcing full prompt re-processing", text)),
        "lack_cache": len(re.findall(r"lack of cache data", text)),
        "oom": len(re.findall(r"out of memory|OOM|failed to allocate", text, re.IGNORECASE)),
    }


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
    log_flags = parse_log(args.log) if args.log else {}

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
        "## 短请求测试 (100 次)",
        "",
    ]
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
    lines.append("")

    Path(args.output).write_text("\n".join(lines), encoding="utf-8")
    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
