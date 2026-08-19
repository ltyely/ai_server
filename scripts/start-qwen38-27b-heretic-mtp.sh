#!/usr/bin/env bash
set -euo pipefail
source /home/yi/data/ai_server/configs/qwen38-27b-heretic-mtp.env
LOG_DIR="/home/yi/data/ai_server/logs/qwen38-heretic-mtp"
mkdir -p "$LOG_DIR"
export LD_LIBRARY_PATH="/home/yi/data/ai_server/bin:${LD_LIBRARY_PATH:-}"
exec /home/yi/data/ai_server/bin/llama-server \
  -m "$MODEL_PATH" \
  --mmproj "$MMPROJ_PATH" \
  --alias "$ALIAS" \
  --host "$HOST" --port "$PORT" \
  -c "$CTX_SIZE" \
  -fa 1 \
  --fit off \
  -ngl -1 \
  --parallel 1 \
  --spec-type draft-mtp --spec-draft-n-max "$DRAFT_N_MAX" \
  --batch-size 2048 --ubatch-size 512 \
  -ctk q8_0 -ctv q4_1 \
  --no-mmap \
  --tensor-split 0 \
  --ctx-checkpoints 69 \
  --repeat-penalty 1.1 --repeat-last-n 64 \
  --temp 0.4 --top-p 0.95 --top-k 20 \
  --cache-ram 32768 \
  --reasoning off \
  --jinja \
  "$@" >> "$LOG_DIR/llm-qwen38-27b-heretic-mtp.log" 2>&1
