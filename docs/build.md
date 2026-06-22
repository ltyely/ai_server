# llama-server 编译记录

## 稳定版（当前）

- 源码路径：`/home/yi/data/ai_server/llama.cpp`
- Commit：`721354fbdfb7743e2be2183d918a3cdb9276c70f`
- 版本号：1076
- 编译器：GNU 13.3.0
- Build Type：Release
- 构建目录：`/home/yi/data/ai_server/llama.cpp/build-new`
- Binary 路径：`/home/yi/data/ai_server/bin/llama-server`
- 升级原因：原 commit `81df3f7cf` 不支持 `--spec-type draft-mtp`，无法启用模型内置 MTP 投机解码。

## 历史版本

- Commit：`81df3f7cfaa6f99de14e792b38d5771bf427383e`
- 版本号：8855
- 状态：已弃用，仅 NextN/MTP 张量保留但未用于投机解码

## CMake 参数

```bash
-DGGML_HIP=ON \
-DGGML_HIP_MMQ_MFMA=ON \
-DGGML_HIP_ROCWMMA_FATTN=OFF \
-DGGML_CUDA=OFF \
-DCMAKE_BUILD_TYPE=Release
```

## 验证项

- [x] `llama-server --version` 可执行
- [x] 识别到 Radeon RX 7900 XTX (gfx1100)
- [x] GGML_HIP_MMQ_MFMA=ON
- [x] GGML_HIP_ROCWMMA_FATTN=OFF
- [x] `--spec-type draft-mtp` 被识别并启用 MTP draft context

## 版本输出

```text
version: 1076 (721354fbd)
built with GNU 13.3.0 for Linux x86_64
```
