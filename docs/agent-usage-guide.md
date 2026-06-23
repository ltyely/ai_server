:# Agent 调用指南：qwen36-27b-daily-mtp-65k

> **版本**：stable-daily-mtp-65k-v1  
> **默认后端**：`qwen36-27b-daily-mtp-65k`  
> **API**：`http://<vm-ip>:11435/v1`  
> **模型文件**：`Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf`

本文档面向需要调用本 LLM 的 Agent / 客户端开发者。

---

## 1. 模型基本信息

| 属性 | 值 |
|------|-----|
| 模型名称 | `qwen36-27b-daily-mtp-65k` |
| 基础模型 | Qwen3.6-27B-Uncensored |
| 参数量 | 27B |
| 量化方式 | Q4_K_P |
| 文件大小 | ~17.99 GB |
| 上下文窗口 | 65536 tokens（默认，已固化） |
| 训练上下文 | 262144 tokens |
| 推理后端 | llama.cpp server |
| llama.cpp commit | `721354fbdfb7743e2be2183d918a3cdb9276c70f` |
| 运行环境 | Radeon RX 7900 XTX (gfx1100), ROCm 7.2.2 |
| 启动方式 | `sudo systemctl start llm-qwen36-27b-daily-mtp.service` |

---

## 2. 模型特点

### 2.1 内置 MTP（Multi-Token Prediction）投机解码

- 启动参数：`--spec-type draft-mtp --spec-draft-n-max 3`
- 模型 GGUF 内部包含 NextN/MTP 张量，llama-server 会自动使用。
- **效果**：
  - MTP 平均命中率：~77%
  - 平均接受长度：~3.32 tokens
  - 最高可达 100% 命中率
  - 各位置命中率：position 0: 0.873, position 1: 0.762, position 2: 0.683
- **收益**：显著提升 decode 阶段吞吐，降低首 token 后整体生成延迟。

### 2.2 Reasoning / Thinking 已关闭

- 启动参数：`--reasoning off`
- 模型不会输出 `<think>...</think>` 等思考过程（但 chat template 仍保留相关占位，模型内部不会展开）。
- **影响**：
  - 输出更直接，不会泄漏内部推理链。
  - 适合需要直接答案、JSON、工具调用的场景。
  - 如需复杂推理，可在 system prompt 中明确要求"step by step"。

### 2.3 KV Cache 量化

- 启动参数：`-ctk q4_0 -ctv q4_0`
- Key/Value cache 均量化为 q4_0。
- **收益**：在 24GB VRAM 下支持 65K context。
- **代价**：极长上下文下可能对精度有轻微影响，但基线测试未观察到质量下降。

### 2.4 Flash Attention

- 启动参数：`-fa 1`
- 使用 ROCm HIP Flash Attention 实现。

### 2.5 No MMAP

- 启动参数：`--no-mmap`
- 模型权重完整加载到显存/内存，避免运行时磁盘 IO 抖动。

---

## 3. 性能指标

> 数据来自基线测试与 server log。

| 指标 | 值 |
|------|-----|
| **短请求 P95 延迟** | 3.60 s |
| **短请求平均延迟** | 1.81 s |
| **JSON 可解析率** | 100% (50/50) |
| **TTFT mean** | 1827.76 ms |
| **TTFT p95** | 9601.27 ms |
| **TTFT max（60K context）** | 115645.59 ms (~115 s) |
| **Prompt eval speed mean** | 141.57 tokens/s |
| **Prompt eval speed p95** | 512.23 tokens/s |
| **Generation eval speed mean** | 93.12 tokens/s |
| **TG speed mean** | 47.77 t/s |
| **TG speed p95** | 54.95 t/s |
| **MTP acceptance mean** | 0.77 |
| **MTP acceptance p95** | 1.00 |
| **VRAM 峰值** | 21.2 GB / 24 GB |
| **OOM** | 0 次 |

### 3.1 上下文长度与 TTFT 参考

| Prompt tokens | 平均 TTFT |
|---------------|-----------|
| ~8K           | ~6 s |
| ~16K          | ~10 s |
| ~32K          | ~21 s |
| ~60K          | ~42 s |

---

## 4. 局限性

### 4.1 硬件与环境

- **GPU**：仅单卡 Radeon RX 7900 XTX (24GB VRAM)。
- **ROCm**：当前使用 ROCm 7.2.2，未安装 ROCm 7.14 / TheRock。
- **XNACK**：内核未启用 XNACK，仅通过环境变量 `HSA_XNACK=1` 设置，实际效果有限。
- **VRAM 上限**：峰值约 21.2GB，接近 24GB 上限，进一步增大 context 或 KV 精度可能 OOM。

### 4.2 Context 与长会话

- **默认 context**：65536 tokens。
- **真实 Agent 长会话**：经 task1 A/B 测试验证，逐步累积到 60K tokens 时未触发 full prompt re-processing。
- **上下文剧烈切换**：同一 slot 中频繁切换 8K/16K/32K/60K 等差异较大的 prompt 长度，可能触发 full prompt re-processing（基线测试中出现 25 次）。
- **建议**：Agent 调用时尽量复用同一 slot，避免同一对话中 prompt 长度剧烈变化。

### 4.3 视觉与 longvision-128k

- **longvision-128k 不可用**：`qwen36-27b-longvision-128k` 已降级为实验性后端，不作为备选默认。
- **原因**：
  - 128K context + mmproj 在 24GB VRAM 下 OOM。
  - 64K/32K context 长文本 prefill 极慢（<35 t/s），60K prompt 处理超过 10 分钟。
- **影响**：当前仅支持文本输入，不支持图片输入。

### 4.4 Top-K 采样器 fallback

- 日志中可能出现：`device 'ROCm0' does not have support for op TOP_K needed for sampler 'top-k'`
- **影响**：top-k 采样操作部分在 CPU 上执行，对短请求影响极小，对高并发可能有轻微影响。

### 4.5 量化影响

- Q4_K_P 量化在大多数任务下质量接近原模型，但极端代码/数学推理任务可能略逊于更高精度版本。

---

## 5. 调用方法

### 5.1 确认服务运行

```bash
curl http://localhost:11435/v1/models
```

### 5.2 curl 示例

```bash
curl http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test" \
  -d '{
    "model": "qwen36-27b-daily-mtp-65k",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "解释什么是 MTP 投机解码。"}
    ],
    "temperature": 0.4,
    "max_tokens": 512,
    "top_p": 0.95,
    "top_k": 20,
    "repeat_penalty": 1.1
  }'
```

### 5.3 Python 示例

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-test",
)

response = client.chat.completions.create(
    model="qwen36-27b-daily-mtp-65k",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "用 Python 写一个快速排序。"},
    ],
    temperature=0.4,
    max_tokens=512,
    top_p=0.95,
    extra_body={"top_k": 20, "repeat_penalty": 1.1},
)
print(response.choices[0].message.content)
```

### 5.4 JSON / 工具调用示例

```python
response = client.chat.completions.create(
    model="qwen36-27b-daily-mtp-65k",
    messages=[
        {"role": "system", "content": "只输出合法 JSON，不要解释。"},
        {"role": "user", "content": "调用 calculator，参数 a=3, b=5"},
    ],
    temperature=0.2,
    max_tokens=128,
    response_format={"type": "json_object"},
)
```

- 基线测试 JSON 可解析率：100%。
- 建议 JSON 任务 temperature 0.2-0.4，system prompt 明确要求"只输出 JSON"。

---

## 6. 最佳实践

### 6.1 Prompt 长度管理

- **短请求**（<2K）：延迟 1-4s，适合高频调用。
- **中上下文**（8K-32K）：TTFT 6-21s，适合文档分析。
- **长上下文**（60K）：TTFT ~42s，上限 ~115s，适合长文档总结。
- **超过 65K**：会被截断，建议分段处理或改用其他后端。

### 6.2 Agent 长会话

- 使用同一 `session`/`slot`，让上下文自然累积。
- 避免在同一 slot 中突然切换超大/超小 prompt。
- 如需清空上下文，建议开启新对话/新 slot，而非发送超短 prompt 覆盖。

### 6.3 Sampling 参数建议

| 场景 | temperature | top_p | top_k | repeat_penalty |
|------|-------------|-------|-------|----------------|
| 日常问答 | 0.4-0.7 | 0.95 | 20 | 1.1 |
| JSON/工具调用 | 0.2-0.4 | 0.95 | 20 | 1.1 |
| 代码生成 | 0.2-0.4 | 0.95 | 20 | 1.05-1.1 |
| 创意写作 | 0.7-1.0 | 0.95 | 50 | 1.0-1.05 |

### 6.4 超时设置

- 短请求：建议 timeout 30s。
- 中上下文（32K）：建议 timeout 120s。
- 长上下文（60K）：建议 timeout 180-300s。

---

## 7. 故障排查

### 7.1 服务未响应

```bash
systemctl status llm-qwen36-27b-daily-mtp.service
sudo systemctl restart llm-qwen36-27b-daily-mtp.service
```

### 7.2 OOM 或模型加载失败

- 检查 VRAM：
  ```bash
  amd-smi monitor
  ```
- 确认无其他 llama-server 实例占用显存。
- 当前 stable 配置已接近 VRAM 上限，不建议同时启动其他大模型。

### 7.3 输出出现 thinking 标签

- 当前配置 `--reasoning off`，理论上不会输出 `<think>`。
- 如出现，检查是否调用了其他模型或 longvision 服务。

### 7.4 JSON 解析失败

- 降低 temperature 到 0.2-0.4。
- system prompt 明确："只输出合法 JSON，不要解释，不要 markdown code fence"。
- 必要时使用 `response_format={"type": "json_object"}`。

---

## 8. 相关文档

- `docs/services.md`：服务状态与切换方法
- `docs/models.md`：模型来源与 SHA256
- `docs/tuning-matrix.md`：调优矩阵与 context size A/B 结论
- `docs/change-log.md`：版本变更记录
- `benchmarks/baseline-report.md`：基线测试报告
- `benchmarks/tuning/context-size-ab.md`：context size A/B 测试报告
