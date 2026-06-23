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

## 已解决的问题

3. **systemd 服务安装**
   - 影响：当前 Agent 没有无密码 sudo 权限，`pkexec` 也无法在无图形认证代理环境下使用。
   - 方案：用户提供 sudo 口令，完成服务安装与启用。
   - 状态：已解决。
     - `llm-qwen36-27b-daily-mtp.service`：已安装、已启用、已启动
     - `llm-qwen36-27b-longvision-128k.service`：已安装、已禁用

## 已解决的问题

4. **长会话中出现 full prompt re-processing**
   - 影响：基线测试期间 server log 出现 25 次 `forcing full prompt re-processing due to lack of cache data`。
   - 方案：通过 task1 的 32K/49K/65K context size A/B 测试验证，真实 Agent 长会话（上下文逐步增长）未触发 re-processing。基线测试中的 25 次主要由于同一 slot 中频繁切换 8K/16K/32K/60K 不同长度 prompt 导致。
   - 状态：已降级为可控风险，不阻止使用 65K 默认 context。

5. **longvision-128k 实用性评估**
   - 影响：需求文档 §4 将 longvision-128k 设计为备选后端，但当前硬件无法满足。
   - 方案：经测试确认 24GB VRAM 下 128K+mmproj OOM，64K/32K 长文本 prefill 极慢，已将其降级为实验性后端，保持服务 disabled，不作为备选默认。
   - 状态：已处理。

## 未解决的问题 / 风险

1. **ROCm 7.14 / TheRock 未安装**
   - 影响：需求文档 §5.6 默认候选为 ROCm 7.14 / TheRock，但当前环境仅安装 ROCm 7.2.2。
   - 当前处理：环境变量使用 ROCm 7.2.2，保留 7.14 回退路径注释。
   - 建议：如需按需求默认 7.14，需单独安装 ROCm 7.14 或 TheRock，并进行 A/B 测试。

2. **XNACK 当前内核未启用**
   - 影响：`rocminfo` 显示 `XNACK enabled: NO`，但环境变量设置 `HSA_XNACK=1`。
   - 当前处理：保留环境变量设置，等待实际运行观察是否生效或是否需要内核参数开启。
   - 建议：如出现显存分配问题，可尝试在 grub 中开启 XNACK 并重启。

3. **llama.cpp 版本升级风险**
   - 影响：原 commit `81df3f7cf` 不支持 `--spec-type draft-mtp`，已升级到 `721354fbdfb7743e2be2183d918a3cdb9276c70f`。
   - 风险：最新 master 可能存在未发现的稳定性问题，需持续观察。

## 待人工确认事项

- [x] 是否接受从 `crotron/...-Balanced-MTP` 下载模型（已确认）。
- [x] 是否接受 systemd 服务已安装并启用 daily-mtp（已确认）。
- [ ] 是否需要安装 ROCm 7.14 / TheRock 并重新编译 llama-server。
- [ ] 是否需要开启内核 XNACK 参数。
- [ ] 是否需要升级 GPU 显存以启用 longvision-128k。
