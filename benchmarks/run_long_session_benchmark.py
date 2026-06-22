#!/usr/bin/env python3
"""长会话 Agent 模拟：30 轮，逐步累积上下文。"""
import argparse
import json
import time
from bench_client import ChatClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11435")
    parser.add_argument("--model", default="qwen36-27b-daily-mtp-65k")
    parser.add_argument("--rounds", type=int, default=30)
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/long-session-result.json")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    messages = [
        {"role": "system", "content": "你是一个能记住上下文的助手。每次回答都要基于之前的对话。"}
    ]
    results = []
    total_tokens = 0

    for i in range(args.rounds):
        user_msg = f"第 {i+1} 轮：请简要复述你记得的所有关键信息，并补充一句关于本地推理后端部署的建议。"
        messages.append({"role": "user", "content": user_msg})
        try:
            start = time.time()
            r = client.chat(messages, max_tokens=256)
            elapsed = time.time() - start
            total_tokens = r["total_tokens"]
            messages.append({"role": "assistant", "content": r["content"]})
            results.append({
                "round": i + 1,
                "ok": True,
                "elapsed": elapsed,
                "total_tokens": total_tokens,
                "content_preview": r["content"][:200],
            })
        except Exception as e:
            results.append({
                "round": i + 1,
                "ok": False,
                "error": str(e),
            })
            break

    summary = {
        "rounds": len(results),
        "successful_rounds": sum(1 for r in results if r["ok"]),
        "final_total_tokens": total_tokens,
        "mean_elapsed": sum(r["elapsed"] for r in results if r["ok"]) / max(1, sum(1 for r in results if r["ok"])),
        "max_elapsed": max((r["elapsed"] for r in results if r["ok"]), default=0),
    }
    output = {"summary": summary, "results": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Long session benchmark: {summary}")


if __name__ == "__main__":
    main()
