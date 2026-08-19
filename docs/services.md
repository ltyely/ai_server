# 服务说明

## 默认后端（稳定）

### `llm-qwen36-27b-daily-mtp-65k.service`

| 属性 | 值 |
|------|-----|
| 描述 | Qwen3.6 27B Daily MTP 65K llama-server |
| 状态 | **已启用、正在运行** |
| 模型 | `qwen36-27b-daily-mtp-65k` |
| 模型文件 | `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf` |
| API | `http://<vm-ip>:11435/v1` |
| Context size | 65536（默认，已固化） |
| 启动命令 | `sudo systemctl start llm-qwen36-27b-daily-mtp.service` |
| 启用命令 | `sudo systemctl enable llm-qwen36-27b-daily-mtp.service` |

这是当前稳定默认后端，已通过完整基线与长会话测试。

## Qwen3.8 实验性后端

### `llm-qwen38-27b-heretic-mtp.service`

| 属性 | 值 |
|------|-----|
| 描述 | Qwen3.8 27B Heretic MTP llama-server |
| 状态 | **实验性，需手动切换** |
| 模型 | `qwen38-27b-heretic-mtp` |
| 模型文件 | `RVN-Q4_K_M-mtp.gguf` |
| mmproj 文件 | `mmproj-Qwen3.8-27B-Q8_0.gguf` |
| API | `http://<vm-ip>:11436/v1` |
| Context size | 65536 / 98304 / 131072（通过 `configs/qwen38-27b-heretic-mtp.env` 调整） |
| 启动命令 | `/home/yi/data/ai_server/scripts/use-qwen38-heretic-mtp.sh` |
| 切回默认 | `/home/yi/data/ai_server/scripts/use-qwen36-daily-mtp.sh` |

**限制**：
- 需要 llama.cpp v0.1.2+（`1511ce3bc`）
- ROCm 下性能低于 Qwen3.6（详见 `docs/qwen38-evaluation.md`）
- 长上下文 prefill 速度随长度急剧下降
- 128K 可启动但剩余 VRAM 仅约 3GB

## 旧实验性后端（已废弃）

### `llm-qwen36-27b-longvision-128k.service`

| 属性 | 值 |
|------|-----|
| 描述 | Qwen3.6 27B LongVision 128K MTP MM llama-server |
| 状态 | **已禁用，模型文件已删除** |
| 模型 | `qwen36-27b-longvision-128k` |
| 模型文件 | 已删除 |
| mmproj 文件 | 已删除 |

**废弃原因**：
- 24GB VRAM 下 128K context + mmproj OOM
- 64K/32K context 长文本 prefill 极慢（<35 t/s）
- 不具备实用价值

## 服务切换

```bash
# 切回 Qwen3.6 默认后端（推荐）
/home/yi/data/ai_server/scripts/use-qwen36-daily-mtp.sh

# 切换到 Qwen3.8 实验性后端
/home/yi/data/ai_server/scripts/use-qwen38-heretic-mtp.sh
```

## 服务文件位置

- `/home/yi/data/ai_server/services/llm-qwen36-27b-daily-mtp.service`
- `/home/yi/data/ai_server/services/llm-qwen38-27b-heretic-mtp.service`
- `/home/yi/data/ai_server/services/llm-qwen36-27b-longvision-128k.service`（已废弃）
- 已安装到 `/etc/systemd/system/`
