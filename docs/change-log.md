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

### 相关文档

- `docs/services.md`
- `docs/tuning-matrix.md`
- `benchmarks/baseline-report.md`
- `benchmarks/tuning/context-size-ab.md`
- `docs/issues.md`
- `docs/work-report.md`
