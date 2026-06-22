#!/bin/bash
th/Qwen3.6-27B-GGUF

# ==========================================
# AMD ROCm / 7900 XTX 专属底层环境优化
# ==========================================
export HSA_OVERRIDE_GFX_VERSION=11.0.0
# 禁用 SDMA 内存拷贝，PVE 直通环境下的免死金牌
export HSA_ENABLE_SDMA=0

# ==========================================
# 路径配置
# ==========================================
MODEL_PATH="/home/yi/data/ai_server/models"
BIN_PATH="/home/yi/data/ai_server/llama.cpp/build/bin/llama-server"

# 确保极限内存锁定权限生效
ulimit -l unlimited
ulimit -n 65535

echo "启动 Qwen-3.6-27B Dense 生产级单卡 Agent 节点..."

$BIN_PATH \
  -m "$MODEL_PATH/Qwen3.6-27B-Q4_K_M.gguf" \
  -c 16384 \
  -b 256 \
  -ub 256 \
  -ngl 99 \
  -t 4 \
  --no-mmap \
  --flash-attn on \
  --reasoning off \
  --parallel 1 \
  --chat-template-kwargs '{"preserve_thiking": true}'\
  --host 0.0.0.0 \
  --port 5580
