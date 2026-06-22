# 最终工作报告

## 项目概述

完成 Homelab Qwen3.6-27B 本地推理后端 v0.2 的部署、基线测试与文档化工作。

## 完成项

- [x] 模型下载与校验
  - 主力：`Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf`
  - 备选主模型：`Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q5_K_P.gguf`
  - mmproj：`mmproj-Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-f16.gguf`
  - 全部计算 SHA256 并记录到 `docs/models.md`
- [x] llama-server 编译
  - 因原 commit `81df3f7cf` 不支持 `--spec-type draft-mtp`，升级至 `721354fbdfb7743e2be2183d918a3cdb9276c70f`
  - 编译参数：`GGML_HIP=ON`, `GGML_HIP_MMQ_MFMA=ON`, `GGML_HIP_ROCWMMA_FATTN=OFF`
- [x] 启动脚本与 systemd 服务
  - `scripts/start-qwen36-27b-daily-mtp.sh`
  - `scripts/start-qwen36-27b-longvision-128k.sh`
  - `scripts/use-daily-mtp.sh`
  - `scripts/use-longvision-128k.sh`
  - `services/llm-qwen36-27b-daily-mtp.service`
  - `services/llm-qwen36-27b-longvision-128k.service`
- [x] 环境变量与配置
  - `configs/qwen36-27b-daily-mtp.env`
  - `configs/qwen36-27b-longvision-128k.env`
- [x] 基线测试
  - 短请求 100 次
  - JSON/工具调用 50 次
  - 中长上下文 8K/16K/32K/60K
  - 长会话 Agent 模拟（累积到 60K tokens）
- [x] 文档
  - `docs/models.md`
  - `docs/build.md`
  - `docs/tuning-matrix.md`
  - `docs/issues.md`
  - `benchmarks/baseline-report.md`
- [x] Git 版本控制
  - 初始化 `/home/yi/data/ai_server/.git`
  - `.gitignore` 忽略模型、binary、日志等
  - 关键里程碑已提交 commit

## 默认状态

- 服务：daily-mtp 计划启用，longvision 不启用
  - 注意：systemd 服务文件尚未安装到 `/etc/systemd/system/`，需用户手动执行
- 默认 API：`http://<vm-ip>:11435/v1`
- 默认模型：`qwen36-27b-daily-mtp-65k`
- 备选 API：`http://<vm-ip>:11436/v1`
- 备选模型：`qwen36-27b-longvision-128k`

## 测试结果摘要

| 测试项 | 结果 |
|--------|------|
| 短请求 100 次 | 成功率 100/100，平均延迟 1.81s，P95 3.60s |
| JSON 可解析率 | 50/50 = 100%（≥95% 通过） |
| 8K 上下文 | 成功 3/3，平均 6.13s |
| 16K 上下文 | 成功 3/3，平均 10.29s |
| 32K 上下文 | 成功 3/3，平均 20.64s |
| 60K 上下文 | 成功 3/3，平均 42.11s |
| 长会话 60K | 14 轮成功，最大单轮 24.60s |
| VRAM 峰值 | 21.2GB / 24GB（≤22.5GB 通过） |
| OOM | 0 次 |
| full prompt re-processing | 25 次（需关注） |

## 主要问题与风险

1. systemd 服务需要 root 权限安装，当前未能自动完成。
2. ROCm 7.14 / TheRock 未安装，实际使用 ROCm 7.2.2。
3. XNACK 内核未启用。
4. server log 中出现 25 次 full prompt re-processing，建议后续调优 context size。

## 后续建议

1. **立即**：手动安装 systemd 服务并启用 daily-mtp。
2. **第一优先级**：按 `docs/tuning-matrix.md` 进行稳定性确认，重点观察长会话是否频繁 re-prefill。
3. **第二优先级**：尝试 context size 32K/49K/65K 的 A/B，找到re-prefill 和性能的甜点。
4. **第三优先级**：如需 ROCm 7.14 / TheRock，单独安装并 A/B 测试。
5. **第四优先级**：测试备选 longvision-128k 的 128K 上下文和 mmproj 视觉能力。

## 文件位置

- 项目根目录：`/home/yi/data/ai_server/`
- 工作目录副本：`/home/yi/data/workspace/inbox/local_llm/issues.md` 和 `work-report.md`
