# 基线测试报告

生成时间：2026-06-22T18:39:30.447720

## 测试环境

- GPU: Radeon RX 7900 XTX (gfx1100)
- VRAM: 24560 MB
- ROCm: 7.2.2 (当前环境未安装 7.14 / TheRock)
- llama.cpp commit: 721354fbdfb7743e2be2183d918a3cdb9276c70f
- Model: qwen36-27b-daily-mtp-65k

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

- full_reprocess: 25
- lack_cache: 25
- oom: 0

## 结论

- JSON 解析率 >= 95%，通过最低验收。
