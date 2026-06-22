# llama-server 编译记录

## 稳定版

- 源码路径：`/home/yi/data/ai_server/llama.cpp`
- Commit：`81df3f7cfaa6f99de14e792b38d5771bf427383e`
- 版本号：8855
- 编译器：GNU 13.3.0
- Build Type：Release
- 构建目录：`/home/yi/data/ai_server/llama.cpp/build`
- Binary 路径：`/home/yi/data/ai_server/bin/llama-server`
- 复制时间：$(date -Iseconds)

## CMake 参数

```bash
-DGGML_HIP=ON \
-DGGML_HIP_MMQ_MFMA=ON \
-DGGML_HIP_ROCWMMA_FATTN=OFF \
-DGGML_CUDA=OFF
```

## 验证项

- [x] `llama-server --version` 可执行
- [x] 识别到 Radeon RX 7900 XTX (gfx1100)
- [x] GGML_HIP_MMQ_MFMA=ON
- [x] GGML_HIP_ROCWMMA_FATTN=OFF
ggml_cuda_init: found 1 ROCm devices (Total VRAM: 24560 MiB):
  Device 0: Radeon RX 7900 XTX, gfx1100 (0x1100), VMM: no, Wave Size: 32, VRAM: 24560 MiB
version: 8855 (81df3f7cf)
built with GNU 13.3.0 for Linux x86_64
