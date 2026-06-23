:# ai_server 文档中心

本文档目录包含 Homelab Qwen3.6-27B 本地推理后端的设计、测试、调优与运维记录。

## 稳定版本

- **版本名称**：stable-daily-mtp-65k-v1
- **Git tag**：`stable-daily-mtp-65k-v1`
- **唯一推荐默认后端**：`qwen36-27b-daily-mtp-65k`
- **默认 API**：`http://<vm-ip>:11435/v1`
- **默认 context size**：65536

## 文档索引

| 文件 | 内容 |
|------|------|
| `README.md` | 本文档，项目总览与索引 |
| `models.md` | 模型来源、文件名、SHA256、禁止替代清单 |
| `build.md` | llama-server 编译记录与 CMake 参数 |
| `services.md` | systemd 服务说明、默认状态、切换方法 |
| `tuning-matrix.md` | 调优纪律、测试矩阵、context size A/B 结论 |
| `issues.md` | 已知问题、风险与待确认事项 |
| `change-log.md` | 每次保留的调优参数与版本变更 |
| `work-report.md` | 最终工作报告与验收结果 |

## 关键结论

1. **daily-mtp-65k 是唯一推荐默认后端**。
2. **默认 context size 65536** 已在 32K/49K/65K A/B 测试中验证为最优。
3. **longvision-128k 标记为实验/不可实用**，在当前 24GB VRAM 下无法同时满足 128K context + mmproj。
4. 真实 Agent 长会话（逐步累积上下文）不易触发 full prompt re-processing；剧烈切换上下文长度才会触发。

## 测试报告

- `benchmarks/baseline-report.md`：基线测试结果
- `benchmarks/tuning/context-size-ab.md`：context size A/B 测试报告
