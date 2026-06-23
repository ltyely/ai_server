:# ai_server

Homelab Qwen3.6-27B 本地推理后端（stable v1）。

## 唯一推荐默认后端

- **服务**：`llm-qwen36-27b-daily-mtp-65k.service`
- **模型**：`qwen36-27b-daily-mtp-65k`
- **API**：`http://<vm-ip>:11435/v1`
- **Context size**：65536（默认，已固化）
- **启动命令**：`sudo systemctl start llm-qwen36-27b-daily-mtp.service`

`qwen36-27b-daily-mtp-65k` 是当前唯一推荐用于日常、Agent、长上下文的默认后端。该配置已通过基线测试与 32K/49K/65K context size A/B 测试验证。

## 实验性后端（不推荐日常使用）

- **服务**：`llm-qwen36-27b-longvision-128k.service`
- **状态**：已安装，但**已禁用**，不作为备选默认
- **原因**：在当前 24GB VRAM（Radeon RX 7900 XTX）下不具备实用价值
  - 128K context + mmproj 启动即 OOM
  - 64K/32K context 长文本 prefill 极慢（<35 t/s），60K prompt 处理超过 10 分钟
- **如需启动**（仅限实验）：`/home/yi/data/ai_server/scripts/use-longvision-128k.sh`
- **任务完成后必须切回**：`/home/yi/data/ai_server/scripts/use-daily-mtp.sh`

## 目录说明

- `bin/`：llama-server 稳定版 binary
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

# 人工触发实验性后端（不推荐日常使用）
/home/yi/data/ai_server/scripts/use-longvision-128k.sh

# 切回默认后端
/home/yi/data/ai_server/scripts/use-daily-mtp.sh
```

## 版本

- Git tag：`stable-daily-mtp-65k-v1`
- llama.cpp commit：`721354fbdfb7743e2be2183d918a3cdb9276c70f`
