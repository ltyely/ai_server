# 模型文件记录

## 主力方案：日常高速 MTP 后端

| 项目 | 内容 |
|------|------|
| 模型名称 | 日常高速 MTP 后端 |
| 系统名 | qwen36-27b-daily-mtp-65k |
| 文件名 | `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf` |
| 来源仓库 | `crotron/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP` |
| 原始指定仓库 | `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Balanced`（该仓库不存在 MTP 文件） |
| 存放路径 | `/home/yi/data/ai_server/models/qwen3.6-27b/daily-mtp-65k/` |
| 文件大小 | 17987600544 bytes (~17.99 GB) |
| SHA256 | `8f784a3762da816920648fe39505cb0a1085e19579b2a0ce5344e92eebb75a30` |
| 下载时间 | 2026-06-22 |

### 禁止替代文件

- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-Q4_K_P.gguf`
- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-IQ4_XS.gguf`
- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-Q5_K_P.gguf`
- `Huihui-Qwen3.6-27B-abliterated.Q4_K_M.gguf`

---

## 备选方案：长上下文视觉实验后端

### 主模型

| 项目 | 内容 |
|------|------|
| 模型名称 | 长上下文视觉实验后端 |
| 系统名 | qwen36-27b-longvision-128k |
| 文件名 | `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q5_K_P.gguf` |
| 来源仓库 | `crotron/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP` |
| 原始指定仓库 | `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Balanced`（该仓库不存在 MTP 文件） |
| 存放路径 | `/home/yi/data/ai_server/models/qwen3.6-27b/longvision-128k/` |
| 文件大小 | 待补充 |
| SHA256 | 待补充 |
| 下载时间 | 2026-06-22 |

### mmproj

| 项目 | 内容 |
|------|------|
| 文件名 | `mmproj-Qwen3.6-27B-Uncensored-HauhauCS-Aggressive-f16.gguf` |
| 来源仓库 | `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive` |
| 存放路径 | `/home/yi/data/ai_server/models/qwen3.6-27b/longvision-128k/` |
| 文件大小 | 884M |
| SHA256 | `082ca68e4a53ce72ae934a11cdd54cf18d3dde6ac63c5d5a75a92bfacf7db430` |
| 下载时间 | 2026-06-22 |

### 禁止替代主模型

- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-Q5_K_P.gguf`
- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-Q4_K_P.gguf`
- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP-Q4_K_P.gguf`
- `Qwen3.6-27B-Uncensored-HauhauCS-Balanced-IQ4_XS.gguf`

### 禁止替代 mmproj

- `mmproj-Qwen3.6-27B-Uncensored-HauhauCS-Balanced-f16.gguf`（除非人工确认并单独测试）

---

## 下载说明

- 由于原始指定仓库 `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Balanced` 中不存在 `-MTP-` 文件，Agent 执行了搜索并报告候选文件。
- 候选仓库 `crotron/Qwen3.6-27B-Uncensored-HauhauCS-Balanced-MTP` 中的 MTP 文件名与需求文档完全一致。
- 经用户确认后，从候选仓库下载了主力和备选主模型。
- mmproj 按需求从 `HauhauCS/Qwen3.6-27B-Uncensored-HauhauCS-Aggressive` 下载。
