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

- 服务：`llm-qwen36-27b-daily-mtp.service` 已安装、已启用、正在运行
- 服务：`llm-qwen36-27b-longvision-128k.service` 已安装、已禁用、不自动启动
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

## 性能观测结果（来自 server log）

| 指标 | 统计值 |
|------|--------|
| **首 token 加载时间 / TTFT** | count=206, mean=1827.76 ms, p95=9601.27 ms, max=115645.59 ms（60K 上下文） |
| **Prompt eval 速度** | count=206, mean=141.57 tokens/s, p95=512.23 tokens/s, max=742.34 tokens/s |
| **Generation eval 速度** | count=412, mean=93.12 tokens/s, p95=432.90 tokens/s |
| **TG speed（实时解码吞吐）** | count=80, mean=47.77 t/s, p95=54.95 t/s, max=55.35 t/s |
| **MTP 投机解码命中率** | count=206, mean=0.77, p95=1.00 |
| **MTP 平均接受长度** | count=206, mean=3.32 tokens |
| **MTP 各位置命中率** | position 0: 0.873, position 1: 0.762, position 2: 0.683 |

### 观测说明

- **TTFT** 对应 server log 中的 `prompt eval time`，即 prompt 进入后到首个 token 生成前的 prefill 耗时。短 prompt 约 100-300 ms，60K 上下文约 115 s，仍在 120 s 阈值内。
- **TG speed** 是 llama-server 生成过程中周期性打印的 `tg = XX.XX t/s`，比平均 generation eval 速度更能反映实时解码吞吐，稳定在 45-55 t/s。
- **MTP 投机解码命中率** 通过 `draft acceptance = X.XXXX (X accepted / Y generated)` 统计，平均 77%，最高可达 100%，平均接受长度 3.32 tokens，说明 draft-mtp 显著提升了 decode 效率。

## 主要问题与风险

1. ROCm 7.14 / TheRock 未安装，实际使用 ROCm 7.2.2。
2. XNACK 内核未启用。
3. server log 中出现 25 次 full prompt re-processing，建议后续调优 context size。

## 后续建议

1. **第一优先级**：按 `docs/tuning-matrix.md` 进行稳定性确认，重点观察长会话是否频繁 re-prefill。
3. **第二优先级**：尝试 context size 32K/49K/65K 的 A/B，找到re-prefill 和性能的甜点。
4. **第三优先级**：如需 ROCm 7.14 / TheRock，单独安装并 A/B 测试。
5. **第四优先级**：测试备选 longvision-128k 的 128K 上下文和 mmproj 视觉能力。

## 文件位置

- 项目根目录：`/home/yi/data/ai_server/`
- 工作目录副本：`/home/yi/data/workspace/inbox/local_llm/issues.md` 和 `work-report.md`
