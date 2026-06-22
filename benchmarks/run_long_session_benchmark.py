#!/usr/bin/env python3
"""长会话 Agent 模拟：逐步累积上下文到 40K/50K/60K。"""
import argparse
import json
import time
from bench_client import ChatClient


def make_long_text(token_count: int):
    base = "人工智能本地推理后端部署测试。模型使用 Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf，启用 draft-mtp 投机解码。 "
    repeat = max(1, int(token_count / (len(base) * 0.5)))
    return (base * repeat)[: int(token_count / 0.5)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11435")
    parser.add_argument("--model", default="qwen36-27b-daily-mtp-65k")
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/long-session-result.json")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    messages = [
        {"role": "system", "content": "你是一个能记住上下文的助手。每次回答都要基于之前的对话，并简要复述关键信息。"}
    ]
    results = []
    target_levels = [40000, 50000, 60000]
    reached_levels = []
    total_tokens = 0
    round_num = 0

    while True:
        round_num += 1
        # 每轮发送一个约 4000 tokens 的文本，要求总结并补充建议
        long_text = make_long_text(4000)
        user_msg = f"第 {round_num} 轮：请阅读以下文本并总结关键信息，同时补充一条本地推理后端部署建议。\n\n{long_text}\n\n总结："
        messages.append({"role": "user", "content": user_msg})

        try:
            start = time.time()
            r = client.chat(messages, max_tokens=512)
            elapsed = time.time() - start
            total_tokens = r["total_tokens"]
            messages.append({"role": "assistant", "content": r["content"]})
            results.append({
                "round": round_num,
                "ok": True,
                "elapsed": elapsed,
                "total_tokens": total_tokens,
                "content_preview": r["content"][:200],
            })
            print(f"Round {round_num}: total_tokens={total_tokens}, elapsed={elapsed:.2f}s")

            for level in target_levels:
                if total_tokens >= level and level not in reached_levels:
                    reached_levels.append(level)
                    print(f"  -> reached {level} tokens")

            if total_tokens >= 60000:
                break
        except Exception as e:
            results.append({
                "round": round_num,
                "ok": False,
                "error": str(e),
            })
            break

        # 安全上限
        if round_num >= 60:
            break

    summary = {
        "rounds": len(results),
        "successful_rounds": sum(1 for r in results if r["ok"]),
        "final_total_tokens": total_tokens,
        "reached_levels": reached_levels,
        "mean_elapsed": sum(r["elapsed"] for r in results if r["ok"]) / max(1, sum(1 for r in results if r["ok"])),
        "max_elapsed": max((r["elapsed"] for r in results if r["ok"]), default=0),
    }
    output = {"summary": summary, "results": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Long session benchmark: {summary}")


if __name__ == "__main__":
    main()
