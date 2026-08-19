:# ai_server

Homelab Qwen3.6/3.8-27B 本地推理后端。

## 默认后端（稳定）

- **服务**：`llm-qwen36-27b-daily-mtp-65k.service`
- **模型**：`qwen36-27b-daily-mtp-65k`
- **API**：`http://<vm-ip>:11435/v1`
- **Context size**：65536（默认，已固化）
- **启动命令**：`sudo systemctl start llm-qwen36-27b-daily-mtp.service`

`qwen36-27b-daily-mtp-65k` 是当前稳定默认后端，已通过完整基线与长会话测试。

## Qwen3.8 实验性后端

- **服务**：`llm-qwen38-27b-heretic-mtp.service`
- **模型**：`qwen38-27b-heretic-mtp`
- **API**：`http://<vm-ip>:11436/v1`
- **Context size**：65536 / 98304 / 131072 可配置
- **启动命令**：`/home/yi/data/ai_server/scripts/use-qwen38-heretic-mtp.sh`
- **切回默认**：`/home/yi/data/ai_server/scripts/use-qwen36-daily-mtp.sh`

**注意**：Qwen3.8 需要 llama.cpp v0.1.2+，当前 ROCm 下性能低于 Qwen3.6，详见 `docs/qwen38-evaluation.md`。

## 旧实验性后端（已废弃）

- **服务**：`llm-qwen36-27b-longvision-128k.service`
- **状态**：已禁用，模型文件已删除
- **原因**：24GB VRAM 下不具备实用价值

## 目录说明

- `bin/`：llama-server 稳定版 binary（已用 `patchelf` 修正 RUNPATH，自包含，不依赖 `llama.cpp/build-new/`）
- `bin-candidate/`：候选版本 binary
- `configs/`：环境变量文件
- `scripts/`：启动与切换脚本
- `services/`：systemd 服务文件
- `models/`：GGUF 模型文件（被 gitignore 忽略）
- `logs/`：服务日志
- `benchmarks/`：测试报告
- `docs/`：模型记录、change-log、调优矩阵、服务说明

## 快速开始

```bash
# 启动默认后端（推荐）
sudo systemctl start llm-qwen36-27b-daily-mtp.service

# 查看状态
systemctl status llm-qwen36-27b-daily-mtp.service

# 切换到 Qwen3.8 实验性后端
/home/yi/data/ai_server/scripts/use-qwen38-heretic-mtp.sh

# 切回 Qwen3.6 默认后端
/home/yi/data/ai_server/scripts/use-qwen36-daily-mtp.sh
```

## 版本

- Git tag：`stable-daily-mtp-65k-v1`
- llama.cpp commit：`1511ce3bc`（v0.1.2，Qwen3.8 兼容）
- 旧版 commit：`721354fbdfb7743e2be2183d918a3cdb9276c70f`（仅 Qwen3.6）
