#!/usr/bin/env bash
set -euo pipefail

echo "[!] 人工触发备选后端：longvision-128k"
echo "[!] 注意：该服务仅供实验，任务完成后必须执行 use-daily-mtp.sh 切回默认后端"

sudo systemctl stop llm-qwen36-27b-daily-mtp.service || true
sudo systemctl start llm-qwen36-27b-longvision-128k.service

echo "[*] 备选后端已启动"
echo "    Base URL: http://$(hostname -I | awk '{print $1}'):11436/v1"
echo "    Model:    qwen36-27b-longvision-128k"
