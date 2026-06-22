#!/usr/bin/env bash
set -euo pipefail

# 加载环境变量
source /home/yi/data/ai_server/configs/qwen36-27b-longvision-128k.env

# 确保日志目录存在
LOG_DIR="/home/yi/data/ai_server/logs/longvision-128k"
mkdir -p "$LOG_DIR"

# 确保 llama-server 能找到本地 .so
export LD_LIBRARY_PATH="/home/yi/data/ai_server/bin:${LD_LIBRARY_PATH:-}"

exec /home/yi/data/ai_server/bin/llama-server \
  -m /home/yi/data/ai_server/models/qwen3.6-27b/longvision-128k/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q5_K_P.gguf \
  --mmproj /home/yi/data/ai_server/models/qwen3.6-27b/longvision-128k/mmproj-Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-f16.gguf \
  --alias qwen36-27b-longvision-128k \
  --host 0.0.0.0 \
  --port 11436 \
  -c 131072 \
  --parallel 1 \
  -b 2048 \
  -ub 512 \
  -fa 1 \
  -ngl 99 \
  -t 16 \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  --cache-type-k q5_0 \
  --cache-type-v q4_1 \
  --no-mmap \
  --temp 0.4 \
  --top-p 0.95 \
  --top-k 20 \
  "$@" \
  >> "$LOG_DIR/llm-qwen36-27b-longvision-128k.log" 2>&1
