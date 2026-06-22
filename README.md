# ai_server

Homelab Qwen3.6-27B 本地推理后端部署目录。

## Preset

- `daily-mtp-65k`：日常高速 MTP 后端，端口 11435
- `longvision-128k`：长上下文视觉实验后端，端口 11436（仅人工触发）

## 目录说明

- `bin/`：llama-server 稳定版 binary
- `bin-candidate/`：候选版本 binary
- `configs/`：环境变量文件
- `scripts/`：启动与切换脚本
- `services/`：systemd 服务文件
- `models/`：GGUF 模型文件（被 gitignore 忽略）
- `logs/`：服务日志
- `benchmarks/`：测试报告
- `docs/`：模型记录、change-log、调优矩阵

## 快速开始

```bash
# 启动默认后端
sudo systemctl start llm-qwen36-27b-daily-mtp.service

# 人工触发备选后端
/home/yi/data/ai_server/scripts/use-longvision-128k.sh

# 切回默认后端
/home/yi/data/ai_server/scripts/use-daily-mtp.sh
```
