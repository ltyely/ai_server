#!/usr/bin/env python3
"""Context size A/B 测试：在指定 context size 下运行长会话并收集指标。"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bench_client import ChatClient


def make_long_text(token_count: int):
    base = "人工智能本地推理后端部署测试。模型使用 Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf，启用 draft-mtp 投机解码。 "
    repeat = max(1, int(token_count / (len(base) * 0.5)))
    return (base * repeat)[: int(token_count / 0.5)]


def start_server(ctx_size: int, log_file: str, port: int = 11435):
    """启动指定 context size 的 llama-server。"""
    env = os.environ.copy()
    env["ROCM_PATH"] = "/opt/rocm-7.2.2"
    env["LD_LIBRARY_PATH"] = f"/home/yi/data/ai_server/bin:/opt/rocm-7.2.2/lib:/opt/rocm-7.2.2/llvm/lib:{env.get('LD_LIBRARY_PATH', '')}"
    env["HSA_XNACK"] = "1"
    env["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

    cmd = [
        "/home/yi/data/ai_server/bin/llama-server",
        "-m", "/home/yi/data/ai_server/models/qwen3.6-27b/daily-mtp-65k/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf",
        "--alias", f"qwen36-27b-daily-mtp-{ctx_size}",
        "--host", "0.0.0.0",
        "--port", str(port),
        "-c", str(ctx_size),
        "-fa", "1",
        "--spec-type", "draft-mtp",
        "--spec-draft-n-max", "3",
        "--batch-size", "2048",
        "--ubatch-size", "512",
        "-ctk", "q4_0",
        "-ctv", "q4_0",
        "--no-mmap",
        "--tensor-split", "0",
        "--reasoning", "off",
        "--ctx-checkpoints", "69",
        "--repeat-penalty", "1.1",
        "--repeat-last-n", "64",
        "--temp", "0.4",
        "--top-p", "0.95",
        "--top-k", "20",
    ]

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = open(log_file, "w", encoding="utf-8")
    proc = subprocess.Popen(cmd, stdout=log_fh, stderr=subprocess.STDOUT, env=env)
    return proc, log_fh


def wait_for_server(url: str, timeout: float = 120.0):
    client = ChatClient(url, "test")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if client.is_ready(timeout=2.0):
            return True
        time.sleep(1)
    return False


def parse_log_metrics(log_file: str):
    import re
    text = Path(log_file).read_text(encoding="utf-8", errors="ignore")
    stats = {
        "ttft_ms": [],
        "gen_tps": [],
        "tg_tps": [],
        "mtp_acceptance": [],
    }
    for m in re.finditer(r"prompt eval time\s*=\s*([\d.]+)\s*ms", text):
        stats["ttft_ms"].append(float(m.group(1)))
    for m in re.finditer(r"\s+eval time\s*=\s*[\d.]+\s*ms\s*/\s*[\d]+\s*tokens.*?([\d.]+)\s*tokens per second", text):
        stats["gen_tps"].append(float(m.group(1)))
    for m in re.finditer(r"n_decoded\s*=\s*\d+,\s*tg\s*=\s*([\d.]+)\s*t/s", text):
        stats["tg_tps"].append(float(m.group(1)))
    for m in re.finditer(r"draft acceptance\s*=\s*([\d.]+)", text):
        stats["mtp_acceptance"].append(float(m.group(1)))

    flags = {
        "full_reprocess": len(re.findall(r"forcing full prompt re-processing", text)),
        "lack_cache": len(re.findall(r"lack of cache data", text)),
        "oom": len(re.findall(r"out of memory|OOM|failed to allocate", text, re.IGNORECASE)),
    }
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


def run_long_session(url: str, model: str, target_tokens: int, max_rounds: int = 60):
    client = ChatClient(url, model)
    if not client.is_ready(timeout=5):
        raise RuntimeError("Server not ready")

    messages = [
        {"role": "system", "content": "你是一个能记住上下文的助手。每次回答都要基于之前的对话，并简要复述关键信息。"}
    ]
    results = []
    total_tokens = 0
    round_num = 0

    while total_tokens < target_tokens and round_num < max_rounds:
        round_num += 1
        long_text = make_long_text(3000)
        user_msg = f"第 {round_num} 轮：请阅读以下文本并总结关键信息，同时补充一条本地推理后端部署建议。\n\n{long_text}\n\n总结："
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
                "content_preview": r["content"][:100],
            })
            print(f"  Round {round_num}: total_tokens={total_tokens}, elapsed={elapsed:.2f}s")
        except Exception as e:
            results.append({
                "round": round_num,
                "ok": False,
                "error": str(e),
            })
            break

    return results


def get_vram_peak():
    try:
        import subprocess
        out = subprocess.check_output(["amd-smi", "monitor"], stderr=subprocess.DEVNULL, text=True, timeout=5)
        lines = out.strip().splitlines()
        for line in lines:
            if "VRAM" in line or "%" in line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    return float(parts[1])  # 假设第二列是 VRAM used MB
                except ValueError:
                    continue
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ctx", type=int, required=True)
    parser.add_argument("--port", type=int, default=11435)
    parser.add_argument("--target-tokens", type=int, default=60000)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    log_file = f"/home/yi/data/ai_server/logs/tuning/context-{args.ctx}.log"
    print(f"[*] 启动 context size {args.ctx} 测试，日志：{log_file}")
    proc, log_fh = start_server(args.ctx, log_file, port=args.port)

    try:
        print("[*] 等待服务就绪...")
        if not wait_for_server(f"http://localhost:{args.port}", timeout=120):
            raise RuntimeError("Server failed to start")
        print("[*] 服务已就绪")

        print(f"[*] 运行长会话测试，目标 {args.target_tokens} tokens...")
        results = run_long_session(f"http://localhost:{args.port}", f"qwen36-27b-daily-mtp-{args.ctx}", args.target_tokens)

        # 等待日志写入
        time.sleep(2)
        log_fh.flush()

        stats, flags = parse_log_metrics(log_file)
        output = {
            "ctx_size": args.ctx,
            "target_tokens": args.target_tokens,
            "rounds": len(results),
            "successful_rounds": sum(1 for r in results if r["ok"]),
            "final_total_tokens": results[-1]["total_tokens"] if results else 0,
            "mean_round_elapsed": sum(r["elapsed"] for r in results if r["ok"]) / max(1, sum(1 for r in results if r["ok"])),
            "max_round_elapsed": max((r["elapsed"] for r in results if r["ok"]), default=0),
            "ttft_ms": summarize(stats["ttft_ms"]),
            "gen_tps": summarize(stats["gen_tps"]),
            "tg_tps": summarize(stats["tg_tps"]),
            "mtp_acceptance": summarize(stats["mtp_acceptance"]),
            "flags": flags,
            "raw_results": results,
        }
    finally:
        print("[*] 停止服务...")
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log_fh.close()

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[*] 结果已保存：{args.output}")
    print(json.dumps({k: v for k, v in output.items() if k != "raw_results"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
