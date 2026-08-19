#!/usr/bin/env bash
set -euo pipefail
source /home/yi/data/ai_server/configs/qwen38-27b-heretic-mtp-vulkan.env
LOG_DIR="/home/yi/data/ai_server/logs/qwen38-heretic-mtp-vulkan"
mkdir -p "$LOG_DIR"
export LD_LIBRARY_PATH="/home/yi/data/ai_server/bin-vulkan:${LD_LIBRARY_PATH:-}"
export GGML_VK_DISABLE_HOST_VISIBLE_VIDMEM=1
exec /home/yi/data/ai_server/bin-vulkan/llama-server \
  -m "$MODEL_PATH" \
  --mmproj "$MMPROJ_PATH" \
  --alias "$ALIAS" \
  --host "$HOST" --port "$PORT" \
  -c "$CTX_SIZE" \
  -fa 1 \
  --fit off \
  -ngl -1 \
  --parallel 1 \
  --device Vulkan0 \
  --spec-type draft-mtp --spec-draft-n-max "$DRAFT_N_MAX" \
  --batch-size 2048 --ubatch-size 512 \
  -ctk q8_0 -ctv q4_1 \
  --no-mmap \
  --ctx-checkpoints 69 \
  --repeat-penalty 1.1 --repeat-last-n 64 \
  --temp 0.4 --top-p 0.95 --top-k 20 \
  --reasoning off \
  --jinja \
  "$@" >> "$LOG_DIR/llm-qwen38-27b-heretic-mtp-vulkan.log" 2>&1
