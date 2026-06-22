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

1. **systemd 服务需要 root 权限安装**
   - 影响：当前 Agent 没有无密码 sudo 权限，`pkexec` 也无法在无图形认证代理环境下使用。
   - 当前处理：服务文件已生成并验证语法正确，但未安装到 `/etc/systemd/system/`。
   - 建议：用户需手动执行以下命令完成安装：
     ```bash
     sudo cp /home/yi/data/ai_server/services/*.service /etc/systemd/system/
     sudo systemctl daemon-reload
     sudo systemctl enable llm-qwen36-27b-daily-mtp.service
     sudo systemctl start llm-qwen36-27b-daily-mtp.service
     # 确认 longvision 不启用
     sudo systemctl disable llm-qwen36-27b-longvision-128k.service
     ```

2. **ROCm 7.14 / TheRock 未安装**
   - 影响：需求文档 §5.6 默认候选为 ROCm 7.14 / TheRock，但当前环境仅安装 ROCm 7.2.2。
   - 当前处理：环境变量使用 ROCm 7.2.2，保留 7.14 回退路径注释。
   - 建议：如需按需求默认 7.14，需单独安装 ROCm 7.14 或 TheRock，并进行 A/B 测试。

3. **XNACK 当前内核未启用**
   - 影响：`rocminfo` 显示 `XNACK enabled: NO`，但环境变量设置 `HSA_XNACK=1`。
   - 当前处理：保留环境变量设置，等待实际运行观察是否生效或是否需要内核参数开启。
   - 建议：如出现显存分配问题，可尝试在 grub 中开启 XNACK 并重启。

4. **llama.cpp 版本升级**
   - 影响：原 commit `81df3f7cf` 不支持 `--spec-type draft-mtp`，无法启用模型内置 MTP 投机解码。
   - 当前处理：已升级到 `721354fbdfb7743e2be2183d918a3cdb9276c70f`，MTP 生效。
   - 风险：最新 master 可能存在未发现的稳定性问题，需持续观察。

5. **长会话中出现 full prompt re-processing**
   - 影响：基线测试期间 server log 出现 25 次 `forcing full prompt re-processing due to lack of cache data`。
   - 当前处理：60K 上下文单轮耗时 42s，未超过 120s 阈值；长会话最大单轮耗时 24.6s。
   - 建议：按需求文档 §5.3，如真实 Agent 长会话中频繁 re-prefill，可测试 49K 或 32K 作为默认 context size。

## 待人工确认事项

- [x] 是否接受从 `crotron/...-Balanced-MTP` 下载模型（已确认）。
- [ ] 是否需要安装 ROCm 7.14 / TheRock 并重新编译 llama-server。
- [ ] 是否需要开启内核 XNACK 参数。
- [ ] 是否接受当前 systemd 服务未自动安装，需手动完成。
- [ ] 是否需要针对 full prompt re-processing 进一步调小默认 context size。
