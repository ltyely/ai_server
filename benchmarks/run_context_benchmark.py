#!/usr/bin/env python3
"""中长上下文测试：8K/16K/32K/60K 各 3 次。"""
import argparse
import json
import time
from bench_client import ChatClient


def make_prompt(token_count: int):
    # 近似的 token 估算：1 token ~ 0.75 个英文单词 或 ~0.5 个汉字
    # 这里使用重复文本填充
    base = "人工智能本地推理后端部署测试。 "
    repeat = max(1, int(token_count / (len(base) * 0.5)))
    text = (base * repeat)[: int(token_count / 0.5)]
    return [
        {"role": "system", "content": "你是一个有帮助的助手。请总结以下文本的核心内容。"},
        {"role": "user", "content": f"请总结以下文本（约 {token_count} tokens）：\n\n{text}\n\n总结："},
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11435")
    parser.add_argument("--model", default="qwen36-27b-daily-mtp-65k")
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/context-result.json")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    results = []
    for ctx in [8192, 16384, 32768, 60000]:
        for run in range(3):
            messages = make_prompt(ctx)
            try:
                start = time.time()
                r = client.chat(messages, max_tokens=128)
                elapsed = time.time() - start
                results.append({
                    "ctx_target": ctx,
                    "run": run + 1,
                    "ok": True,
                    "elapsed": elapsed,
                    "prompt_tokens": r["prompt_tokens"],
                    "completion_tokens": r["completion_tokens"],
                    "content": r["content"][:200],
                })
            except Exception as e:
                results.append({
                    "ctx_target": ctx,
                    "run": run + 1,
                    "ok": False,
                    "error": str(e),
                })

    summary = {}
    for ctx in [8192, 16384, 32768, 60000]:
        ok = [r for r in results if r["ctx_target"] == ctx and r["ok"]]
        summary[str(ctx)] = {
            "success": len(ok),
            "mean_elapsed": sum(r["elapsed"] for r in ok) / len(ok) if ok else None,
            "mean_prompt_tokens": sum(r["prompt_tokens"] for r in ok) / len(ok) if ok else None,
        }

    output = {"summary": summary, "results": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Context benchmark: {summary}")


if __name__ == "__main__":
    main()
