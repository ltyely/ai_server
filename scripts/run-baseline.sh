#!/usr/bin/env bash
set -euo pipefail

# 基线测试入口脚本
# 用法：run-baseline.sh [short|context|long-session|json|all]

MODE="${1:-all}"
BASE_URL="http://localhost:11435/v1"
MODEL="qwen36-27b-daily-mtp-65k"
BENCHMARK_DIR="/home/yi/data/ai_server/benchmarks"
LOG_DIR="/home/yi/data/ai_server/logs/daily-mtp-65k"
REPORT_FILE="$BENCHMARK_DIR/baseline-report.md"

echo "[*] 基线测试模式: $MODE"
echo "[*] API: $BASE_URL"
echo "[*] Model: $MODEL"

mkdir -p "$BENCHMARK_DIR"

case "$MODE" in
  short|all)
    echo "[*] 运行短请求测试 (100次) ..."
    python3 "$BENCHMARK_DIR/run_short_benchmark.py" --url "$BASE_URL" --model "$MODEL" --count 100 --output "$BENCHMARK_DIR/short-result.json"
    ;;
esac

case "$MODE" in
  json|all)
    echo "[*] 运行 JSON/工具调用稳定性测试 (50次) ..."
    python3 "$BENCHMARK_DIR/run_json_benchmark.py" --url "$BASE_URL" --model "$MODEL" --count 50 --output "$BENCHMARK_DIR/json-result.json"
    ;;
esac

case "$MODE" in
  context|all)
    echo "[*] 运行中长上下文测试 ..."
    python3 "$BENCHMARK_DIR/run_context_benchmark.py" --url "$BASE_URL" --model "$MODEL" --output "$BENCHMARK_DIR/context-result.json"
    ;;
esac

case "$MODE" in
  long-session|all)
    echo "[*] 运行长会话 Agent 模拟 ..."
    python3 "$BENCHMARK_DIR/run_long_session_benchmark.py" --url "$BASE_URL" --model "$MODEL" --output "$BENCHMARK_DIR/long-session-result.json"
    ;;
esac

# 生成报告
echo "[*] 生成基线测试报告 ..."
python3 "$BENCHMARK_DIR/generate_report.py" \
  --short "$BENCHMARK_DIR/short-result.json" \
  --json "$BENCHMARK_DIR/json-result.json" \
  --context "$BENCHMARK_DIR/context-result.json" \
  --long-session "$BENCHMARK_DIR/long-session-result.json" \
  --log "$LOG_DIR/llm-qwen36-27b-daily-mtp.log" \
  --output "$REPORT_FILE"

echo "[*] 基线测试完成: $REPORT_FILE"
