# daily-mtp-65k context size A/B 测试报告

> 任务来源：`/home/yi/data/workspace/inbox/local_llm/task1.md`
> 目标：对比 32K / 49K / 65K 三种 context size，判断 full prompt re-processing 是否影响真实 Agent 使用，补测 longvision-128k。

## 测试方法

- 固定参数：ROCm 7.2.2、llama.cpp 721354fbd、KV q4_0/q4_0、MTP n=3、batch 2048/ubatch 512。
- 只修改 `-c`（context size）。
- 长会话模拟：每轮发送约 3000 tokens 文本并要求总结，逐步累积到目标 tokens。
- 收集指标：TTFT、generation speed、TG speed、MTP acceptance、full re-processing 次数、OOM 次数。

## 32K / 49K / 65K 对比表

| 指标 | 32K | 49K | 65K |
|------|-----|-----|-----|
| context size | 32768 | 49152 | 65536 |
| 目标累积 tokens | 30000 | 45000 | 60000 |
| 成功轮数 | 10/10 | 14/14 | 19/19 |
| 最终总 tokens | 32699 | 45855 | 62224 |
| 平均单轮耗时 | 15.70 s | 16.27 s | 16.84 s |
| 最大单轮耗时 | 17.33 s | 18.76 s | 20.67 s |
| TTFT mean | 5768.84 ms | 6447.11 ms | 7276.28 ms |
| TTFT p95 | 7087.65 ms | 8422.93 ms | 10120.43 ms |
| Generation eval speed mean | 305.71 t/s | 281.32 t/s | 257.22 t/s |
| TG speed mean | 43.20 t/s | 44.55 t/s | 45.33 t/s |
| TG speed p95 | 52.44 t/s | 51.16 t/s | 52.72 t/s |
| MTP acceptance mean | 0.616 | 0.683 | 0.758 |
| MTP acceptance p95 | 0.688 | 0.776 | 0.963 |
| full prompt re-processing | 0 | 0 | 0 |
| lack of cache data | 0 | 0 | 0 |
| OOM | 0 | 0 | 0 |

## 结论

### 推荐默认 context

**推荐默认 context size：65536（65K）**

理由：
1. 在真实 Agent 长会话（逐步累积上下文）中，32K/49K/65K 均未触发 full prompt re-processing。
2. 65K 的平均单轮耗时（16.84s）和最大单轮耗时（20.67s）仍在可接受范围，且未超过需求文档 120s 的阈值。
3. 65K 的 MTP 投机解码命中率最高（mean 0.758，p95 0.963），decode 效率优于 32K/49K。
4. TG speed 在三种配置下基本持平（43-45 t/s），说明 context size 对实时生成速度影响有限。

### full prompt re-processing 触发场景

- **本次专门的长会话 A/B 测试（同一 slot，上下文逐步增长）**：未触发。
- **之前的基线测试中出现 25 次 re-processing**：主要由于 8K/16K/32K/60K 上下文测试在同一 slot 中频繁切换不同长度的 prompt，导致 context checkpoint 失效。
- **longvision-128k 测试中出现 re-processing**：长 prompt 处理过程中触发（见下文）。

触发条件总结：
1. 同一 slot 中上下文长度剧烈变化（如从 8K 跳到 60K）。
2. 使用了 SWA / hybrid / recurrent memory 的模型结构，在 cache 不匹配时强制重新处理。
3. 真实 Agent 长会话（逐步增长）不易触发，但仍建议在关键场景监控。

### longvision-128k 补测结果

| 测试项 | 结果 |
|--------|------|
| 64K context 文本（不带 mmproj） | 可启动，但 60K prompt 处理极慢（>10 分钟），未跑完 |
| 100K context 文本（不带 mmproj） | 可启动，预计比 64K 更慢，未实际跑完 |
| 128K context + mmproj 单图 | **OOM 无法启动**（mmproj 需额外 884MB，超出 24GB VRAM） |
| 32K context 文本 | 可启动，但长 prompt 处理仍极慢（~3 分钟处理 6K tokens） |

#### longvision 问题分析

- Q5_K_P 模型（21.26 GB）比 Q4_K_P（17.99 GB）大，且 KV cache 使用 q5_0/q4_1，显存和带宽压力更高。
- 在 24GB VRAM 的 RX 7900 XTX 上，longvision 无法同时满足 128K context + mmproj。
- 即使降级到 64K/32K context，长文本 prefill 速度也不具备实用价值（<35 t/s 在 6K 以上 prompt）。

#### 建议

- 若需使用 longvision-128k，建议：
  - 升级到更大显存的 GPU（≥32GB）。
  - 或改用 Q4_K_P 量化版本（如果存在）。
  - 或仅用于短上下文/单图任务，并降低 context size 到 16K-32K。

## 原始数据文件

- `benchmarks/tuning/context-32k.json`
- `benchmarks/tuning/context-49k.json`
- `benchmarks/tuning/context-65k.json`
- `benchmarks/tuning/longvision-64k-context.json`（未生成，测试超时）
- `benchmarks/tuning/longvision-32k-context.json`（未生成，测试超时）
- 日志：`logs/tuning/context-32768.log`、`context-49152.log`、`context-65536.log`、`longvision-64k.log`、`longvision-32k.log`
