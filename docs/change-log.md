:# 变更日志（Change Log）

## stable-daily-mtp-65k-v1

**日期**：2026-06-23  
**Git tag**：`stable-daily-mtp-65k-v1`

### 固化配置

- **默认后端**：`qwen36-27b-daily-mtp-65k`
- **服务**：`llm-qwen36-27b-daily-mtp.service`（enabled，running）
- **Context size**：65536
- **模型**：`Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf`
- **mmproj**：无
- **KV cache**：`-ctk q4_0 -ctv q4_0`
- **MTP**：`--spec-type draft-mtp --spec-draft-n-max 3`
- **Batch**：`--batch-size 2048 --ubatch-size 512`
- **Sampling**：`--temp 0.4 --top-p 0.95 --top-k 20 --repeat-penalty 1.1 --repeat-last-n 64`
- **llama.cpp commit**：`721354fbdfb7743e2be2183d918a3cdb9276c70f`
- **ROCm**：7.2.2

### 保留原因

1. 基线测试通过：JSON 解析率 100%，VRAM 峰值 21.2GB/24GB，OOM 0 次。
2. 100 次短请求全部成功，P95 延迟 3.60s。
3. 8K/16K/32K/60K 上下文全部成功，60K 平均 42.11s。
4. 长会话 Agent 模拟累积到 60K tokens，14 轮全部成功，最大单轮 24.60s。
5. context size A/B 测试（32K/49K/65K）确认 65K 最优：
   - 真实 Agent 长会话未触发 full prompt re-processing
   - MTP 命中率最高（mean 0.758，p95 0.963）
   - TG speed 稳定（45.33 t/s）

### 降级配置

- **实验性后端**：`qwen36-27b-longvision-128k`
- **服务**：`llm-qwen36-27b-longvision-128k.service`（disabled）
- **降级原因**：
  - 24GB VRAM 下 128K context + mmproj OOM
  - 64K/32K context 长文本 prefill 极慢（<35 t/s），60K prompt 处理超过 10 分钟
- **状态**：不作为备选默认，仅保留文件和脚本供未来硬件升级后实验。

### 仓库清理与 binary 自包含

- **历史脚本清理**：删除 `scripts/fetch_gguf.py`、`hf_search.sh`、`start_api.sh`、`start_q3.6_unsloth.sh`、`start_qwen.sh`。
- **历史模型清理**：删除 `models/` 根目录下所有旧版 GGUF（Qwen3.5、Qwopus、gemma、Qwen3.6-35B、Aggressive-Q4_K_P 等），释放约 130GB 磁盘空间。
- **实验性模型清理**：删除 `models/qwen3.6-27b/longvision-128k/` 及对应 mmproj，释放约 20GB；仅保留脚本/服务文件供未来硬件升级后实验。
- **binary 自包含**：使用 `patchelf` 将 `bin/llama-server` 及所有 `.so` 的 `RUNPATH` 修正为 `/home/yi/data/ai_server/bin:/opt/rocm-7.2.2/lib`，并删除旧版本 `.so`（0.9.11、8783、8855）。`bin/` 不再依赖被 gitignore 的 `llama.cpp/build-new/bin/`。
- **敏感信息复核**：将示例代码中的测试 key `sk-test` 统一替换为 `your-api-key`；未在仓库中发现真实密码、token、私钥。

### 相关文档

- `docs/services.md`
- `docs/tuning-matrix.md`
- `benchmarks/baseline-report.md`
- `benchmarks/tuning/context-size-ab.md`
- `docs/issues.md`
- `docs/work-report.md`
- `docs/agent-usage-guide.md`

## qwen38-heretic-mtp-v1（实验性）

**日期**：2026-08-19  
**状态**：实验性，需手动切换

### 配置

- **模型**：`qwen38-27b-heretic-mtp`
- **模型文件**：`RVN-Q4_K_M-mtp.gguf`（0bserverx Heretic，16 GB）
- **mmproj**：`mmproj-Qwen3.8-27B-Q8_0.gguf`（601 MB）
- **Context size**：65536 / 98304 / 131072 可配置
- **KV cache**：`-ctk q8_0 -ctv q4_1`
- **MTP**：`--spec-type draft-mtp --spec-draft-n-max 5`（扫描 2/3/4/5/6 后选定）
- **Batch**：`--batch-size 2048 --ubatch-size 512`
- **Prompt cache**：`--cache-ram 32768`
- **Sampling**：`--temp 0.4 --top-p 0.95 --top-k 20 --repeat-penalty 1.1 --repeat-last-n 64`
- **Reasoning**：`--reasoning off`（工具调用场景）
- **llama.cpp commit**：`1511ce3bc`（v0.1.2）
- **ROCm**：7.2.2

### 关键变更

1. **升级 llama.cpp 至 v0.1.2**：旧版 `721354fbd` 无法正确加载 Qwen3.8（`missing tensor 'blk.64.ssm_conv1d.weight'`），升级后正常。
2. **binary 替换**：`bin/` 下所有二进制和 `.so` 更新为 v0.1.2，RUNPATH 修正为 `/home/yi/data/ai_server/bin:/opt/rocm-7.2.2/lib`。
3. **新增服务**：`llm-qwen38-27b-heretic-mtp.service`（端口 11436）。
4. **新增切换脚本**：`use-qwen38-heretic-mtp.sh` / `use-qwen36-daily-mtp.sh`。

### 测试结果摘要

- 65K 短请求：100/100 成功，平均 27.4 t/s（优化后 30-46 t/s）
- 65K JSON：50/50 成功
- 96K/128K 可启动，VRAM 占用 21.6GB/22.7GB
- n-max 扫描：5 最优，6 开始下降
- Vulkan 实验：性能极差（0.9 t/s），VM 直通环境下不可用，回退 ROCm
- ROCm 下长上下文 prefill 性能瓶颈明显，128K 实用价值有限

### 相关文档

- `docs/qwen38-evaluation.md`
- `docs/services.md`
