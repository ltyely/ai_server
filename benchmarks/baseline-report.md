:# 基线测试报告

> **状态**：stable-daily-mtp-65k-v1 固化基线
> **Git tag**：`stable-daily-mtp-65k-v1`
> **生成时间**：2026-06-23T00:54:34.078677

## 测试环境

- GPU: Radeon RX 7900 XTX (gfx1100)
- VRAM: 24560 MB
- ROCm: 7.2.2 (当前环境未安装 7.14 / TheRock)
- llama.cpp commit: 721354fbdfb7743e2be2183d918a3cdb9276c70f
- Model: qwen36-27b-daily-mtp-65k
- Context size: 65536（已固化）

## 关键性能指标（来自 server log）

- **首 token 加载时间 / Prompt eval time (TTFT, ms)**: count=206, mean=1827.76, min=93.07, max=115645.59, p95=9601.27
- **Prompt eval 速度 (tokens/s)**: count=206, mean=141.57, min=23.86, max=742.34, p95=512.23
- **Generation eval 速度 (tokens/s)**: count=412, mean=93.12, min=23.86, max=742.34, p95=432.90
- **TG speed (tokens/s)**: count=80, mean=47.77, min=37.56, max=55.35, p95=54.95
- **MTP 投机解码命中率 (acceptance ratio)**: count=206, mean=0.77, min=0.27, max=1.00, p95=1.00
- **MTP 平均接受长度 (mean acceptance length)**: count=206, mean=3.32, min=1.81, max=4.00, p95=4.00
- **MTP 各位置命中率**:
  - position 0: 0.873
  - position 1: 0.762
  - position 2: 0.683

## 短请求测试 (100 次)

- 成功率：100/100
- 平均延迟：1.805s
- P95 延迟：3.602s
- 最小/最大延迟：0.629s / 3.870s
- 总生成 tokens：5581

## JSON / 工具调用稳定性测试 (50 次)

- 成功请求：50/50
- JSON 可解析：50/50
- JSON 解析率：100.0%

## 中长上下文测试

- 8192 tokens: 成功 3/3, 平均耗时 6.13s, 平均 prompt tokens 8238.0
- 16384 tokens: 成功 3/3, 平均耗时 10.29s, 平均 prompt tokens 16431.0
- 32768 tokens: 成功 3/3, 平均耗时 20.64s, 平均 prompt tokens 32815.0
- 60000 tokens: 成功 3/3, 平均耗时 42.11s, 平均 prompt tokens 60047.0

## 长会话 Agent 模拟

- 总轮数：14
- 成功轮数：14
- 最终累计 tokens：60630
- 平均单轮耗时：20.96s
- 最大单轮耗时：24.60s

## Server log 稳定性标记

- full_reprocess_count: 25
- lack_cache_count: 25
- oom_count: 0

## 结论

- JSON 解析率 >= 95%，通过最低验收。
- 60K 上下文 TTFT 在可接受范围内。
- **本基线对应 stable-daily-mtp-65k-v1，是唯一的默认后端推荐配置**。
- full prompt re-processing 25 次主要来源于基线测试中 8K/16K/32K/60K 的频繁切换；真实 Agent 长会话（逐步累积）经 task1 A/B 测试验证不会触发。
- longvision-128k 已被降级为实验性后端，不作为备选默认。
