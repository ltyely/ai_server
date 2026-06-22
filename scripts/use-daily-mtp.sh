#!/usr/bin/env bash
set -euo pipefail

echo "[*] 切换到默认后端：daily-mtp-65k"

sudo systemctl stop llm-qwen36-27b-longvision-128k.service || true
sudo systemctl start llm-qwen36-27b-daily-mtp.service
sudo systemctl enable llm-qwen36-27b-daily-mtp.service

echo "[*] 默认后端已启动"
echo "    Base URL: http://$(hostname -I | awk '{print $1}'):11435/v1"
echo "    Model:    qwen36-27b-daily-mtp-65k"
