#!/usr/bin/env bash
set -euo pipefail

AI_SERVER="/home/yi/data/ai_server"
BUILD_DIR="$AI_SERVER/llama.cpp/build-v012"
BACKUP_DIR="$AI_SERVER/bin-backup-20260622"
BIN_DIR="$AI_SERVER/bin"

echo "=== 1. 备份当前 bin/ ==="
if [ ! -d "$BACKUP_DIR" ]; then
  cp -r "$BIN_DIR" "$BACKUP_DIR"
  echo "已备份到 $BACKUP_DIR"
else
  echo "备份已存在，跳过"
fi

echo "=== 2. 复制新编译的二进制和库 ==="
cp -f "$BUILD_DIR/bin/"llama-* "$BIN_DIR/"
cp -f "$BUILD_DIR/bin/"*.so* "$BIN_DIR/" 2>/dev/null || true
cp -f "$BUILD_DIR/bin/"export-graph-ops "$BIN_DIR/" 2>/dev/null || true

echo "=== 3. 修正 RUNPATH ==="
cd "$BIN_DIR"
for f in llama-* *.so* export-graph-ops; do
  [ -f "$f" ] && patchelf --set-rpath '/home/yi/data/ai_server/bin:/opt/rocm-7.2.2/lib' "$f" 2>/dev/null && echo "patched $f"
done

echo "=== 4. 验证 ==="
unset LD_LIBRARY_PATH
ldd "$BIN_DIR/llama-server" | grep 'not found' || echo "无缺失依赖"

echo "=== 完成 ==="
echo "请手动停止旧服务并启动新服务："
echo "  sudo systemctl stop llm-qwen36-27b-daily-mtp.service"
echo "  /home/yi/data/ai_server/scripts/start-qwen38-27b-heretic-mtp.sh"
