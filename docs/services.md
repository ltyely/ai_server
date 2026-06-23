:# 服务说明

## 默认后端（唯一推荐）

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

这是当前唯一推荐用于日常、Agent、长上下文的默认后端。

## 实验性后端（不推荐日常使用）

### `llm-qwen36-27b-longvision-128k.service`

| 属性 | 值 |
|------|-----|
| 描述 | Qwen3.6 27B LongVision 128K MTP MM llama-server |
| 状态 | **已安装、已禁用** |
| 模型 | `qwen36-27b-longvision-128k` |
| 模型文件 | `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q5_K_P.gguf` |
| mmproj 文件 | `mmproj-Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-f16.gguf` |
| API | `http://<vm-ip>:11436/v1` |
| Context size | 131072（需求设计值） |
| 启动命令 | `/home/yi/data/ai_server/scripts/use-longvision-128k.sh` |
| 当前状态 | `disabled`，不作为备选默认 |

### 为什么 longvision-128k 被降级？

在当前 24GB VRAM（Radeon RX 7900 XTX）环境下，`qwen36-27b-longvision-128k` 不具备实用价值：

1. **128K context + mmproj 启动即 OOM**
   - mmproj 需要额外约 884MB 显存
   - Q5_K_P 主模型（21.26GB）+ 128K KV cache + mmproj 超出 24GB 上限
2. **64K/32K context 长文本 prefill 极慢**
   - 60K prompt 处理超过 10 分钟
   - 6K prompt 处理约 3 分钟
   - prefill 速度 <35 t/s，不具备交互性
3. **不作为备选默认**
   - 为避免误启用，服务保持 `disabled` 状态
   - 如需实验，必须人工执行 `use-longvision-128k.sh`
   - 任务完成后必须执行 `use-daily-mtp.sh` 切回默认后端

## 服务切换

```bash
# 切回默认后端（推荐）
/home/yi/data/ai_server/scripts/use-daily-mtp.sh

# 人工触发实验性后端（不推荐日常使用）
/home/yi/data/ai_server/scripts/use-longvision-128k.sh
```

## 服务文件位置

- `/home/yi/data/ai_server/services/llm-qwen36-27b-daily-mtp.service`
- `/home/yi/data/ai_server/services/llm-qwen36-27b-longvision-128k.service`
- 已安装到 `/etc/systemd/system/`
