#!/bin/bash

# ==========================================
# 7900 XTX 24G + Qwen3.6-35B-A3B 极限压榨稳定版
# ==========================================

# ROCm 基础与防崩优化 (针对 RDNA3 架构)
export HSA_ENABLE_SDMA=0
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export GGML_CUDA_FORCE_MMQ=1
export GGML_ROCM_USE_FA=1
export HIP_VISIBLE_DEVICES=0

# ==========================================
# 路径配置
# ==========================================
MODEL_PATH="/home/yi/data/ai_server/models"
BIN_PATH="/home/yi/data/ai_server/llama.cpp/build/bin/llama-server"

# 权限校验 (解除文件描述符和内存锁定限制)
ulimit -l unlimited
ulimit -n 65535

echo "启动 Qwen3.6-35B-A3B | 7900XTX 显存极限防OOM版..."

# ==========================================
# 核心启动命令参数解析：
# -b/-ub 256       : 保守批处理大小，防止处理长文本时突发显存溢出 (OOM)
# -ngl 99          : 默认尝试全量卸载至显卡
# --flash-attn     : 使用标准长参数开启 Flash Attention，兼容性最好
# --cache-type q4_0: 极致压缩 16K 上下文缓存，为 35B 权重腾出 VRAM
# -t 8             : 为 5600G 分配 8 线程，预留资源给系统和显卡调度
# --jinja 等        : 尝试应用官方 Chat Template 逻辑，保留思维链
# ==========================================

$BIN_PATH \
  -m "$MODEL_PATH/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf" \
  -c 16384 \
  -b 256 \
  -ub 256 \
  -ngl 99 \
  --flash-attn on\
  --parallel 1 \
  --cache-type-k q4_0 \
  --cache-type-v q4_0 \
  -t 8 \
  --jinja \
  --chat-template-kwargs '{"preserve_thinking": true}' \
  --host 0.0.0.0 \
  --port 5580
