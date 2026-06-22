#!/usr/bin/env python3
"""短请求 benchmark：100 次 <2K 上下文请求。"""
import argparse
import json
import time
from bench_client import ChatClient

PROMPTS = [
    {"role": "user", "content": "用一句话解释什么是 MTP（Multi-Token Prediction）？"},
    {"role": "user", "content": "Explain what ROCm is in one sentence."},
    {"role": "user", "content": "写一个 Python 函数，接收一个整数列表并返回其平均值。"},
    {"role": "user", "content": "给出一个查看当前目录下所有文件大小的 shell 命令。"},
    {"role": "user", "content": "请直接输出 JSON：{\"name\":\"llama\",\"type\":\"server\"}"},
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11435")
    parser.add_argument("--model", default="qwen36-27b-daily-mtp-65k")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/short-result.json")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    results = []
    for i in range(args.count):
        prompt = PROMPTS[i % len(PROMPTS)]
        try:
            r = client.chat([prompt], max_tokens=128)
            results.append({
                "index": i,
                "ok": True,
                "elapsed": r["elapsed"],
                "prompt_tokens": r["prompt_tokens"],
                "completion_tokens": r["completion_tokens"],
                "content": r["content"],
            })
        except Exception as e:
            results.append({"index": i, "ok": False, "error": str(e)})
        time.sleep(0.1)

    ok_results = [r for r in results if r["ok"]]
    elapsed_list = [r["elapsed"] for r in ok_results]
    summary = {
        "count": args.count,
        "success": len(ok_results),
        "failed": args.count - len(ok_results),
        "mean_latency": sum(elapsed_list) / len(elapsed_list) if elapsed_list else 0,
        "min_latency": min(elapsed_list) if elapsed_list else 0,
        "max_latency": max(elapsed_list) if elapsed_list else 0,
        "p95_latency": sorted(elapsed_list)[int(len(elapsed_list) * 0.95)] if elapsed_list else 0,
        "total_completion_tokens": sum(r["completion_tokens"] for r in ok_results),
    }
    output = {"summary": summary, "results": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Short benchmark: {summary}")


if __name__ == "__main__":
    main()
