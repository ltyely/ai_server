# 问题记录

## 已解决的问题

1. **HauhauCS 源仓库缺少 `-MTP-` 模型文件**
   - 影响：需求文档 §2.1 指定的 `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Balanced` 仓库中不存在 MTP 文件。
   - 方案：搜索到候选仓库 `crotron/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP`，文件名完全匹配需求，经用户确认后从该仓库下载。
   - 状态：已解决。

2. **huggingface-cli 已废弃**
   - 影响：原 `huggingface-cli repo-files` 等命令不可用。
   - 方案：改用 `hf download` 命令下载模型。
   - 状态：已解决。

## 未解决的问题 / 风险

1. **ROCm 7.14 / TheRock 未安装**
   - 影响：需求文档 §5.6 默认候选为 ROCm 7.14 / TheRock，但当前环境仅安装 ROCm 7.2.2。
   - 当前处理：环境变量使用 ROCm 7.2.2，保留 7.14 回退路径注释。
   - 建议：如需按需求默认 7.14，需单独安装 ROCm 7.14 或 TheRock，并进行 A/B 测试。

2. **XNACK 当前内核未启用**
   - 影响：`rocminfo` 显示 `XNACK enabled: NO`，但环境变量设置 `HSA_XNACK=1`。
   - 当前处理：保留环境变量设置，等待实际运行观察是否生效或是否需要内核参数开启。
   - 建议：如出现显存分配问题，可尝试在 grub 中开启 XNACK 并重启。

3. **长上下文测试耗时较长**
   - 影响：60K 上下文和长会话 Agent 模拟可能耗时数十分钟。
   - 建议：基线测试时可先减少轮数或上下文长度，确认服务基本稳定后再跑完整矩阵。

## 待人工确认事项

- [ ] 是否接受从 `crotron/...-Balanced-MTP` 下载模型（已确认）。
- [ ] 是否需要安装 ROCm 7.14 / TheRock 并重新编译 llama-server。
- [ ] 是否需要开启内核 XNACK 参数。
