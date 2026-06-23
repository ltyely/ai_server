# 最终工作报告

## 项目概述

完成 Homelab Qwen3.6-27B 本地推理后端 v0.2 的部署、基线测试、调优与文档化工作，并固化为 **stable-daily-mtp-65k-v1**。

- **Git tag**：`stable-daily-mtp-65k-v1`
- **唯一推荐默认后端**：`qwen36-27b-daily-mtp-65k`
- **默认 context size**：65536（已固化）
- **实验性后端**：`qwen36-27b-longvision-128k`（已降级，disabled）

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
- [x] task1：daily-mtp-65k 稳定性固化与 context A/B 测试
  - 32K / 49K / 65K context size 长会话 A/B 测试
  - longvision-128k 64K/100K/单图补测
  - 报告：`benchmarks/tuning/context-size-ab.md`
  - 结论已写入 `docs/tuning-matrix.md`
- [x] 文档
  - `docs/models.md`
  - `docs/build.md`
  - `docs/tuning-matrix.md`
  - `docs/issues.md`
  - `benchmarks/baseline-report.md`
  - `benchmarks/tuning/context-size-ab.md`
- [x] Git 版本控制
  - 初始化 `/home/yi/data/ai_server/.git`
  - `.gitignore` 忽略模型、binary、日志等
  - 关键里程碑已提交 commit

## 默认状态

- **服务**：`llm-qwen36-27b-daily-mtp.service` 已安装、已启用、正在运行
- **服务**：`llm-qwen36-27b-longvision-128k.service` 已安装、已禁用、不自动启动
- **默认 API**：`http://<vm-ip>:11435/v1`
- **默认模型**：`qwen36-27b-daily-mtp-65k`
- **默认 context size**：65536
- **实验性 API**：`http://<vm-ip>:11436/v1`（不推荐日常使用）
- **实验性模型**：`qwen36-27b-longvision-128k`（已降级，24GB VRAM 下不具备实用价值）

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

## task1 调优结论（context size A/B）

### 32K / 49K / 65K 对比数据

| 指标 | 32K | 49K | 65K |
|------|-----|-----|-----|
| 目标累积 tokens | 30000 | 45000 | 60000 |
| 成功轮数 | 10/10 | 14/14 | 19/19 |
| 最终总 tokens | 32699 | 45855 | 62224 |
| 平均单轮耗时 | 15.70 s | 16.27 s | 16.84 s |
| 最大单轮耗时 | 17.33 s | 18.76 s | 20.67 s |
| TTFT mean | 5768.84 ms | 6447.11 ms | 7276.28 ms |
| TTFT p95 | 7087.65 ms | 8422.93 ms | 10120.43 ms |
| Generation eval speed mean | 305.71 t/s | 281.32 t/s | 257.22 t/s |
| TG speed mean | 43.20 t/s | 44.55 t/s | 45.33 t/s |
| MTP acceptance mean | 0.616 | 0.683 | **0.758** |
| MTP acceptance p95 | 0.688 | 0.776 | **0.963** |
| full prompt re-processing | 0 | 0 | 0 |
| lack of cache data | 0 | 0 | 0 |
| OOM | 0 | 0 | 0 |

### 推荐默认 context

**daily-mtp-65k 默认 context size：65536（65K）**

- 真实 Agent 长会话（逐步累积上下文）中，32K/49K/65K 均未触发 full prompt re-processing。
- 65K 最大单轮耗时 20.67s，远低于 120s 阈值。
- 65K MTP 命中率最高（mean 0.758，p95 0.963）。
- TG speed 在三种配置下基本持平（43-45 t/s）。

### full prompt re-processing 触发场景

1. 同一 slot 中上下文长度剧烈变化（如基线测试 8K→16K→32K→60K 切换）。
2. longvision 长 prompt 处理中也观察到触发。
3. 真实 Agent 长会话（逐步增长）不易触发。

### longvision-128k 补测结果

| 测试项 | 结果 |
|--------|------|
| 64K context 文本 | 可启动，但 60K prompt 处理极慢（>10 分钟），未跑完 |
| 100K context 文本 | 可启动，预计比 64K 更慢，未实际跑完 |
| 128K context + mmproj 单图 | **OOM 无法启动** |
| 32K context 文本 | 可启动，长 prompt 处理仍极慢（~3 分钟处理 6K tokens） |

**结论**：当前 24GB VRAM 无法支撑 longvision-128k 实用。建议升级 GPU 显存或改用更低量化版本。

## 主要问题与风险

1. ROCm 7.14 / TheRock 未安装，实际使用 ROCm 7.2.2。
2. XNACK 内核未启用。
3. longvision-128k 在当前 24GB VRAM 下不具备实用价值（128K+mmproj OOM，64K/32K 长文本 prefill 极慢），已降级为实验性后端。

## 后续建议

1. **第一优先级**：如需 ROCm 7.14 / TheRock，单独安装并 A/B 测试。
2. **第二优先级**：按 `docs/tuning-matrix.md` 继续 batch/ubatch 调优。
3. **第三优先级**：如需启用 longvision-128k，升级 GPU 显存（≥32GB）或改用更低量化版本。
4. **第四优先级**：持续监控 full prompt re-processing，确认真实 Agent 场景下是否稳定。

## 文件位置

- 项目根目录：`/home/yi/data/ai_server/`
- 工作目录副本：`/home/yi/data/workspace/inbox/local_llm/issues.md` 和 `work-report.md`
