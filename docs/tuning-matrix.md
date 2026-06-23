# 调优测试矩阵

来源：需求文档 §5、§6、§7、§8。

## 调优纪律

1. 先跑 baseline，记录 `benchmarks/baseline-report.md`。
2. 一次只改一类参数。
3. 跑相同测试集。
4. 生成 diff 报告 `benchmarks/tune-<param>.md`。
5. 判断是否保留。
6. 不保留则立即回退。
7. 保留的参数写入 `docs/change-log.md`。

## 参数调优映射

| 需求章节 | 调优参数 | 默认/基线 | 测试范围 | 保留条件 | 回退条件 |
|----------|---------|----------|----------|----------|----------|
| §5.1 MTP | `--spec-draft-n-max` `--spec-type` | `draft-mtp`, `n=3` | n=2/3/4 | 有效速度提升 ≥8%；100 次短请求无崩溃；JSON 可解析率不下降；中文质量无明显下降；长回复无重复 | MTP 接受率明显下降；重复循环；JSON 更容易破坏；更频繁 re-prefill |
| §5.2 KV cache | `-ctk`/`-ctv` | daily: q4_0/q4_0；long: q5_0/q4_1 | q4_0/q4_0, q5_0/q4_1, q8_0/q8_0 | 质量明显提升，速度下降 ≤10%，VRAM ≤22.5GB | VRAM 峰值过高；长上下文 OOM；prefill 明显变慢；速度下降 >15%；质量无收益 |
| §5.3 Context | `-c` | daily: 65536；long: 131072 | daily: 32768/49152/65536；long: 65536/98304/131072 | 速度、稳定性、实际任务需求平衡；默认不追求最大上下文 | 真实长会话频繁 re-prefill；Agent 不稳定 |
| §5.4 Batch | `--batch-size`/`-b` `--ubatch-size`/`-ub` | 2048/512 | 1024/512, 2048/512, 2048/1024, 4096/512 | 长文 TTFT 改善且显存不 OOM | OOM；短 prompt 受影响；32K/60K 不稳定 |
| §5.5 llama.cpp | commit/fork/build 参数 | 81df3f7cf | upstream 新 commit；网友验证 commit；goodbyecain/CainSay fork | 长会话稳定；60K 不触发全量 re-prefill；连续 100 次请求稳定 | 新版本 60K+ 触发全量 re-prefill；JSON 成功率下降；显存泄漏 |
| §5.6 ROCm | ROCm 7.14 / 7.2；HSA_XNACK；HSA_OVERRIDE_GFX_VERSION | ROCm 7.14；HSA_XNACK=1；GFX=11.0.0 | HSA_XNACK=1/unset；ROCm 7.14/7.2 | 能稳定跑 server；decode 快且长会话稳定；无 kernel 错误 | server 模式崩溃；长上下文不稳定；kernel 错误 |
| §5.7 Flash Attention | `-fa 1`；`GGML_HIP_ROCWMMA_FATTN`；`GGML_HIP_MMQ_MFMA` | `-fa 1`；`MMQ_MFMA=ON`；`ROCWMMA=OFF` | 单独构建 binary 测试 ROCWMMA | 真实 server 请求中有稳定收益；无 OOM、无 fallback、无输出异常 | OOM；fallback CPU；生成异常 |
| §5.8 Sampling | `--temp`, `--top-p`, `--top-k`, `--repeat-penalty`, `--repeat-last-n`, reasoning/thinking | daily: temp=0.4, top-p=0.95, top-k=20, repeat-penalty=1.1, repeat-last-n=64, reasoning off | 代码/JSON: temp 0.2～0.4；中文问答：0.4～0.7；开放式写作：0.7～1.0；Agent 工具调用：0.2～0.4 + repeat 1.05～1.15 | JSON 可解析率、工具调用成功率、中文自然度、代码可运行性、MTP 接受率综合提升 | JSON 破坏；工具调用格式失败；输出重复；MTP 接受率下降；输出长度失控 |

## 测试集

### 短请求测试

- 数量：100 次
- 上下文：< 2K
- 内容：中文问答、英文问答、Python 代码、Shell 命令、JSON 输出
- 记录：成功率、平均延迟、P95 延迟、generation tok/s、MTP 接受率、是否重复、是否空 content

### 中长上下文测试

- 8K/16K/32K/60K 各 3 次
- 记录：TTFT、prefill t/s、generation tok/s、VRAM 峰值、是否 full prompt re-processing、OOM、引用正确性

### 长会话 Agent 模拟

- 轮数：30～50 轮
- 累计上下文：逐步增长到 40K、50K、60K
- 记录：每轮 TTFT、每轮总耗时、是否 2～3 分钟卡顿、re-prefill、MTP 接受率变化、显存变化、输出漂移

### JSON / 工具调用稳定性测试

- 数量：50 次
- 要求：合法 JSON、字段完整、无解释文字、无空 content
- 记录：JSON parse 成功率、字段完整率、markdown fence、思考泄漏、重复字段
- 最低验收：默认主力配置 JSON parse 成功率 ≥95%

## 观测方法

### 速度

- `llama-bench`: pp512, tg128, tg512
- server log: prompt eval time, eval time, tokens per second, MTP accepted tokens, MTP acceptance rate
- 客户端总耗时

### 显存

- `amd-smi monitor` 每秒记录
- 至少记录：VRAM used, GPU utilization, GFX clock/SCLK, Memory clock/MCLK, Power, Temperature

### 长会话稳定性

server log 关键词：

```text
forcing full prompt re-processing
lack of cache data
SWA
hybrid/recurrent memory
OOM
out of memory
failed to allocate
slot update
cache miss
content empty
```

## 调优优先级

1. 稳定性确认：服务启动 → 100 次短请求 → 32K → 60K → 长会话 Agent 模拟。
2. 速度优化：llama.cpp commit A/B → KV q4_0/q4_0 vs q5_0/q4_1 → `--spec-draft-n-max` 2/3/4 → batch/ubatch → ROCm 7.14 vs 7.2。
3. 质量优化：sampling → reasoning off/chat_template_kwargs → KV 精度 → context size。
4. 备选能力：128K 启动 → 64K/100K/128K 测试 → mmproj 单图 → 图文混合 → 显存释放与服务切换。

## Context Size A/B 结论（task1）

- **推荐 daily-mtp-65k 默认 context size：65536（65K）**
  - 在真实 Agent 长会话（逐步累积上下文）中，32K/49K/65K 均未触发 full prompt re-processing。
  - 65K 最大单轮耗时 20.67s，远低于 120s 阈值。
  - 65K 的 MTP 命中率最高（mean 0.758，p95 0.963）。
  - TG speed 在三种配置下基本持平（43-45 t/s）。
- **full prompt re-processing 触发场景**：
  - 同一 slot 中上下文长度剧烈变化（如基线测试中 8K→16K→32K→60K 切换）。
  - longvision 长 prompt 处理中也观察到触发。
  - 真实 Agent 长会话（逐步增长）不易触发。
- **longvision-128k 当前状态**：
  - 24GB VRAM 无法同时承载 128K context + mmproj（OOM）。
  - 64K/32K context 文本可启动，但长 prompt prefill 极慢（<35 t/s），不具实用价值。
  - 如需使用 longvision，建议升级 GPU 显存或改用更低量化版本。

详细数据见 `benchmarks/tuning/context-size-ab.md`。
