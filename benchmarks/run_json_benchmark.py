#!/usr/bin/env python3
"""JSON / 工具调用稳定性测试：50 次。"""
import argparse
import json
from bench_client import ChatClient

PROMPTS = [
    "请直接输出合法 JSON，格式：{\"tool\":\"calculator\",\"args\":{\"a\":1,\"b\":2}}，不要任何解释。",
    "输出 JSON：{\"action\":\"search\",\"query\":\"ROCm 7.2\"}，只输出 JSON。",
    "请以 JSON 格式给出结果：{\"name\":\"Qwen3.6\",\"params\":\"27B\"}，不要 markdown。",
]


def is_valid_json(text: str):
    # 去除可能的 markdown code fence
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    try:
        json.loads(cleaned)
        return True, cleaned
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11435")
    parser.add_argument("--model", default="qwen36-27b-daily-mtp-65k")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/json-result.json")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    results = []
    valid_count = 0
    for i in range(args.count):
        prompt = {"role": "user", "content": PROMPTS[i % len(PROMPTS)]}
        try:
            r = client.chat([prompt], temperature=0.2, max_tokens=128)
            valid, detail = is_valid_json(r["content"])
            if valid:
                valid_count += 1
            results.append({
                "index": i,
                "ok": True,
                "valid_json": valid,
                "content": r["content"],
                "detail": detail,
            })
        except Exception as e:
            results.append({"index": i, "ok": False, "error": str(e)})

    summary = {
        "count": args.count,
        "valid_json": valid_count,
        "valid_rate": valid_count / args.count,
        "success": sum(1 for r in results if r["ok"]),
    }
    output = {"summary": summary, "results": results}
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"JSON benchmark: {summary}")


if __name__ == "__main__":
    main()
