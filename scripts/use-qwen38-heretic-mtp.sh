#!/usr/bin/env bash
set -euo pipefail
SERVICE_NAME="llm-qwen38-27b-heretic-mtp.service"
TARGET_SERVICE="llm-qwen36-27b-daily-mtp.service"

echo "=== 切换到 Qwen3.8 Heretic MTP 服务 ==="
echo "停止当前默认服务..."
echo "$SDTK" | sudo -S systemctl stop "$TARGET_SERVICE" 2>/dev/null || true

echo "启动 $SERVICE_NAME..."
echo "$SDTK" | sudo -S systemctl start "$SERVICE_NAME"

sleep 5
echo "=== 服务状态 ==="
systemctl status "$SERVICE_NAME" --no-pager -l
