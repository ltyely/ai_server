# Qwen3.8-27B 评估记录

## 模型选型

| 候选 | 文件 | 大小 | 结论 |
|------|------|------|------|
| 0bserverx Heretic Q4_K_M-mtp | RVN-Q4_K_M-mtp.gguf | 16 GB | **主选**，内置 MTP，mmproj 较小 |
| unsloth 官方 Q4_K_M | Qwen3.8-27B-Q4_K_M.gguf | 16 GB | 对照，无内置 MTP |
| HauhauCS Aggressive-MTP Q4_K_P | - | 17.9 GB | 备选，文件较大 |

## 关键问题与解决

### 1. llama.cpp 版本兼容性问题

**问题**：当前 llama.cpp commit `721354fbd`（2026-06-22）无法正确加载 Qwen3.8。
- `llama-cli` / `llama-bench` 报错：`missing tensor 'blk.64.ssm_conv1d.weight'`
- `llama-server` 虽能加载，但速度异常（2-3 t/s）
- 日志警告：`fused Gated Delta Net (chunked) not supported`

**解决**：升级到 llama.cpp `v0.1.2` / commit `1511ce3bc`（2026-08-18），重新编译 ROCm 版本。
- 编译选项：`BUILD_SHARED_LIBS=ON -DGGML_HIP=ON -DGGML_HIP_GRAPHS=ON -DGGML_HIP_MMQ_MFMA=ON -DGGML_HIP_NO_VMM=ON`
- 使用 `patchelf` 修正 RUNPATH 为 `/home/yi/data/ai_server/bin:/opt/rocm-7.2.2/lib`

**结果**：模型正常加载，速度恢复至 27-45 t/s。

### 2. 多模态投影（mmproj）

- mmproj 文件：`mmproj-Qwen3.8-27B-Q8_0.gguf`（601 MB）
- 加载成功，日志显示 `loaded multimodal model`
- 视觉功能可用，但 `--image-min-tokens 1024` 建议用于 grounding 任务

### 3. reasoning_effort 参数

Qwen3.8 官方支持 `reasoning_effort`：
- `xhigh`（默认）：复杂任务，深度分析
- `medium`：平衡准确性和速度
- `low`：高效推理，优化速度和成本
- `none`：直接回答，无思考

**实测结论**：
- 在当前 llama.cpp v0.1.2 + Heretic 模型组合下，`--chat-template-kwargs '{"reasoning_effort":"..."}'` 对 `<think>` 输出长度影响有限
- `medium` / `low` / `none` 均会产生 `<think>` 标签，区别主要在于思考链详细程度
- **`--reasoning off`** 可将思考链清空为 `<think>\n\n</think>`，是工具调用/JSON 场景的最稳妥选择
- 各档位 decode 速度差异不大（28-40 t/s）

**建议**：Agent / 工具调用场景使用 `--reasoning off`。

## 65K Context 基线测试结果（v0.1.2）

### 短请求（100 次）

| 指标 | 值 |
|------|-----|
| 成功率 | 100/100 |
| 平均延迟 | 3.55 s |
| 平均 completion tokens | 100.26 |
| 平均速度 | 27.4 t/s |

### JSON 输出（50 次）

| 指标 | 值 |
|------|-----|
| 成功率 | 50/50 |
| 平均延迟 | 4.56 s |

### 长链 Agent 模拟测试

- 目标：累积到 120K tokens
- 结果：因服务超时中断，但已验证到 7.4K tokens 累积
- 观察：随上下文累积，prompt 处理速度从 57 t/s 降至 9-19 t/s，eval 从 10.5 t/s 降至 5.7 t/s
- **结论**：Gated DeltaNet 架构下，长上下文 prefill 成本很高，128K 实用价值有限

## 96K / 128K Context 测试

| Context | 启动 | VRAM 占用 | 短请求速度 |
|---------|------|-----------|-----------|
| 65K | 正常 | 20.6 GB / 24 GB | 27-40 t/s |
| 96K | 正常 | 21.6 GB / 24 GB | 30-41 t/s |
| 128K | 正常 | 22.7 GB / 24 GB | 31-40 t/s |

**结论**：128K 在 24GB VRAM 下可启动，但剩余空间仅约 3GB，长 prompt 处理会触发 OOM 或极慢。

## 与帖子数据对比

| 场景 | 帖子（Vulkan） | 本机（ROCm） | 差距 |
|------|---------------|-------------|------|
| 工具调用 decode | 73.4 t/s | 28-41 t/s | ROCm 慢约 40-50% |
| prefill 6.4K | 587 t/s | ~76 t/s（短 prompt） | ROCm 慢约 87% |
| 128K 启动 | 正常 | 正常 | 一致 |

**分析**：
1. ROCm 下 Gated DeltaNet 的 prefill 和 decode 均显著慢于 Vulkan
2. 帖子明确指出 Vulkan decode 比 HIP 快约 29%，本机实测差距更大，可能与 ROCm 7.2.2 对 GDN 的优化不足有关
3. 如需更高性能，建议下一阶段切换 Vulkan 后端

## 推荐配置

```bash
# 当前推荐（ROCm 稳定版）
./scripts/start-qwen38-27b-heretic-mtp.sh

# 关键参数
-c 65536                    # 65K 平衡性能与容量
--reasoning off             # 工具调用场景关闭思考链
--spec-type draft-mtp --spec-draft-n-max 3
-ctk q8_0 -ctv q4_1         # KV cache K8V4
```

## 下一步建议

1. **若需更高性能**：切换 Vulkan 后端（Mesa/RADV），参考帖子配置
2. **若需更长 context**：接受速度损失，或等待 ROCm 对 Gated DeltaNet 的优化
3. **若需更好 JSON/工具调用**：保持 `--reasoning off`，使用 0bserverx Heretic 模型
