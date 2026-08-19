#!/usr/bin/env python3
"""Qwen3.8-27B Heretic MTP 综合 benchmark：基线 / context / 长链 Agent / reasoning_effort。"""
import argparse
import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bench_client import ChatClient


def make_long_text(token_count: int):
    base = "人工智能本地推理后端部署测试。模型使用 Qwen3.8-27B-Heretic-MTP，启用 draft-mtp 投机解码与多模态投影。 "
    repeat = max(1, int(token_count / (len(base) * 0.5)))
    return (base * repeat)[: int(token_count / 0.5)]


def run_short(client, output):
    """100 次短请求。"""
    results = []
    for i in range(100):
        try:
            r = client.chat([{"role": "user", "content": f"请用一句话介绍本地大模型推理后端。序号 {i+1}"}], max_tokens=128)
            results.append({"ok": True, "elapsed": r["elapsed"], "completion_tokens": r["completion_tokens"]})
        except Exception as e:
            results.append({"ok": False, "error": str(e)})
    ok = [r for r in results if r["ok"]]
    summary = {
        "total": len(results),
        "success": len(ok),
        "mean_elapsed": sum(r["elapsed"] for r in ok) / len(ok) if ok else 0,
        "mean_completion_tokens": sum(r["completion_tokens"] for r in ok) / len(ok) if ok else 0,
        "mean_tps": sum(r["completion_tokens"] / r["elapsed"] for r in ok) / len(ok) if ok else 0,
    }
    return {"summary": summary, "results": results}


def run_json(client, output):
    """50 次 JSON 输出。"""
    results = []
    for i in range(50):
        prompt = f"""请生成一个 JSON 对象，包含以下字段：
- id: 整数 {i+1}
- name: 测试项目
- status: 从 [pending, running, completed, failed] 中选择一个
- score: 0 到 100 的随机整数
只输出 JSON，不要其他文字。"""
        try:
            r = client.chat([{"role": "user", "content": prompt}], max_tokens=256)
            content = r["content"].strip()
            # 提取 JSON：支持 markdown 代码块或纯 JSON
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
            try:
                json.loads(json_str)
                valid = True
            except Exception:
                valid = False
            results.append({"ok": valid, "elapsed": r["elapsed"], "content_preview": json_str[:100]})
        except Exception as e:
            results.append({"ok": False, "error": str(e)})
    ok = [r for r in results if r["ok"]]
    summary = {
        "total": len(results),
        "valid_json": len(ok),
        "success_rate": len(ok) / len(results) if results else 0,
        "mean_elapsed": sum(r["elapsed"] for r in ok) / len(ok) if ok else 0,
    }
    return {"summary": summary, "results": results}


def run_context(client, output, levels):
    """长上下文测试：单轮 prompt 逐步增大。"""
    results = []
    for level in levels:
        text = make_long_text(level)
        prompt = f"请阅读以下文本并用一句话总结：\n\n{text}\n\n总结："
        try:
            start = time.time()
            r = client.chat([{"role": "user", "content": prompt}], max_tokens=256)
            elapsed = time.time() - start
            results.append({
                "level": level,
                "ok": True,
                "elapsed": elapsed,
                "prompt_tokens": r["prompt_tokens"],
                "completion_tokens": r["completion_tokens"],
                "total_tokens": r["total_tokens"],
            })
            print(f"Context {level}: prompt_tokens={r['prompt_tokens']}, elapsed={elapsed:.2f}s")
        except Exception as e:
            results.append({"level": level, "ok": False, "error": str(e)})
    return {"results": results}


def run_long_chain(client, output, target_tokens=120000):
    """长链 Agent 模拟：逐步累积上下文到目标 tokens。"""
    messages = [
        {"role": "system", "content": "你是一个 AI 助手，负责协助用户完成多轮任务。每轮请基于之前对话简洁回答，并记住关键信息。"}
    ]
    results = []
    total_tokens = 0
    round_num = 0
    target_levels = [30000, 60000, 90000, 120000]
    reached_levels = []

    while total_tokens < target_tokens and round_num < 80:
        round_num += 1
        long_text = make_long_text(3000)
        user_msg = f"第 {round_num} 轮任务：请阅读以下材料并提取一个关键要点，然后给出下一步行动建议。\n\n{long_text}\n\n回答："
        messages.append({"role": "user", "content": user_msg})

        try:
            start = time.time()
            r = client.chat(messages, max_tokens=384)
            elapsed = time.time() - start
            total_tokens = r["total_tokens"]
            messages.append({"role": "assistant", "content": r["content"]})
            results.append({
                "round": round_num,
                "ok": True,
                "elapsed": elapsed,
                "total_tokens": total_tokens,
                "completion_tokens": r["completion_tokens"],
            })
            print(f"Round {round_num}: total_tokens={total_tokens}, elapsed={elapsed:.2f}s")

            for level in target_levels:
                if total_tokens >= level and level not in reached_levels:
                    reached_levels.append(level)
                    print(f"  -> reached {level} tokens")
        except Exception as e:
            results.append({"round": round_num, "ok": False, "error": str(e)})
            print(f"Round {round_num} failed: {e}")
            break

    summary = {
        "rounds": len(results),
        "successful_rounds": sum(1 for r in results if r["ok"]),
        "final_total_tokens": total_tokens,
        "reached_levels": reached_levels,
        "mean_elapsed": sum(r["elapsed"] for r in results if r["ok"]) / max(1, sum(1 for r in results if r["ok"])),
        "max_elapsed": max((r["elapsed"] for r in results if r["ok"]), default=0),
    }
    return {"summary": summary, "results": results}


def run_reasoning_effort(client, output, efforts):
    """对比不同 reasoning_effort 的速度与输出。"""
    results = []
    test_prompt = "请解释为什么在本地部署大模型时，KV cache 量化位数的分配（K 高 V 低）通常比平均分配更合理。"
    for effort in efforts:
        # 通过 extra_body 传 reasoning_effort（如果 server 支持）
        try:
            start = time.time()
            r = client.chat(
                [{"role": "user", "content": test_prompt}],
                max_tokens=1024,
                extra_body={"reasoning_effort": effort} if hasattr(client, "chat") else None,
            )
            elapsed = time.time() - start
            results.append({
                "effort": effort,
                "ok": True,
                "elapsed": elapsed,
                "completion_tokens": r["completion_tokens"],
                "content_preview": r["content"][:300],
            })
            print(f"reasoning_effort={effort}: elapsed={elapsed:.2f}s, tokens={r['completion_tokens']}")
        except Exception as e:
            results.append({"effort": effort, "ok": False, "error": str(e)})
    return {"results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:11436")
    parser.add_argument("--model", default="qwen38-27b-heretic-mtp")
    parser.add_argument("--output", default="/home/yi/data/ai_server/benchmarks/qwen38/qwen38-result.json")
    parser.add_argument("--test", choices=["short", "json", "context", "long-chain", "reasoning", "all"], default="all")
    parser.add_argument("--context-levels", default="8000,16000,32000,60000")
    parser.add_argument("--long-chain-target", type=int, default=120000)
    parser.add_argument("--reasoning-efforts", default="medium,low")
    args = parser.parse_args()

    client = ChatClient(args.url, args.model)
    if not client.is_ready(timeout=5):
        raise RuntimeError(f"Server not ready at {args.url}")

    results = {}
    if args.test in ("short", "all"):
        print("[*] Running short request benchmark...")
        results["short"] = run_short(client, args.output)
        print(results["short"]["summary"])
    if args.test in ("json", "all"):
        print("[*] Running JSON benchmark...")
        results["json"] = run_json(client, args.output)
        print(results["json"]["summary"])
    if args.test in ("context", "all"):
        print("[*] Running context benchmark...")
        levels = [int(x) for x in args.context_levels.split(",")]
        results["context"] = run_context(client, args.output, levels)
    if args.test in ("long-chain", "all"):
        print("[*] Running long-chain Agent simulation...")
        results["long_chain"] = run_long_chain(client, args.output, args.long_chain_target)
        print(results["long_chain"]["summary"])
    if args.test in ("reasoning", "all"):
        print("[*] Running reasoning_effort comparison...")
        efforts = [x.strip() for x in args.reasoning_efforts.split(",")]
        results["reasoning"] = run_reasoning_effort(client, args.output, efforts)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[*] Results saved to {args.output}")


if __name__ == "__main__":
    main()
