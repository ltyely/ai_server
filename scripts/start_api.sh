#!/bin/bash

# ==========================================
# AMD ROCm / 7900 XTX 专属底层环境优化
# ==========================================
# 强制欺骗驱动，声明为支持的 gfx1100 架构
export HSA_OVERRIDE_GFX_VERSION=11.0.0
# 禁用 SDMA 内存拷贝，防止极限显存下的 PCIe 3.0 页面崩溃
export HSA_ENABLE_SDMA=0 

# ==========================================
# 路径配置 (请确保与你的实际存放位置绝对一致)
# ==========================================
MODEL_PATH="/home/yi/data/ai_server/models"
BIN_PATH="/home/yi/data/ai_server/llama.cpp/build/bin/llama-server"

# 【核心修复 1】解除 Linux 系统的锁定内存限制，防止 hipBLAS 申请内存被拒
ulimit -l unlimited
# 调整最大文件描述符，增强 HTTP 并发稳定性
ulimit -n 65535

echo "启动 Gemma-4-31B-Distill 极限单卡 Agent 节点..."

$BIN_PATH \
  -m "$MODEL_PATH/gemma-4-31B-it-Claude-Opus-Distill.q4_k_m.gguf" \
  -c 8192 \
  -b 128 \
  -ub 128 \
  -ngl 99 \
  --no-mmap \
  -fa on \
  --parallel 1 \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --host 0.0.0.0 \
  --port 5580
