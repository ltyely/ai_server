#!/usr/bin/env bash
set -euo pipefail

# 加载环境变量
source /home/yi/data/ai_server/configs/qwen36-27b-daily-mtp.env

# 确保日志目录存在
LOG_DIR="/home/yi/data/ai_server/logs/daily-mtp-65k"
mkdir -p "$LOG_DIR"

# 确保 llama-server 能找到本地 .so
export LD_LIBRARY_PATH="/home/yi/data/ai_server/bin:${LD_LIBRARY_PATH:-}"

exec /home/yi/data/ai_server/bin/llama-server \
  -m /home/yi/data/ai_server/models/qwen3.6-27b/daily-mtp-65k/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf \
  --alias qwen36-27b-daily-mtp-65k \
  --host 0.0.0.0 \
  --port 11435 \
  -c 65536 \
  -fa 1 \
  --fit off \
  -ngl -1 \
  --parallel 1 \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  --batch-size 2048 \
  --ubatch-size 512 \
  -ctk q8_0 \
  -ctv q4_1 \
  --no-mmap \
  --tensor-split 0 \
  --cache-ram 32768 \
  --reasoning off \
  --ctx-checkpoints 69 \
  --repeat-penalty 1.1 \
  --repeat-last-n 64 \
  --temp 0.4 \
  --top-p 0.95 \
  --top-k 20 \
  --jinja \
  "$@" \
  >> "$LOG_DIR/llm-qwen36-27b-daily-mtp.log" 2>&1
