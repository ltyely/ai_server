import os
from huggingface_hub import HfApi, hf_hub_download

def main():
    print("="*50)
    print("🤖 专属 GGUF 交互式下载器")
    print("="*50)
    
    repo_id = input("\n👉 请输入 Hugging Face 仓库名 (例如 unsloth/Qwen3.5-0.8B-Instruct-GGUF): ").strip()
    if not repo_id:
        return

    api = HfApi()
    print(f"\n🔍 正在查询仓库 [{repo_id}]，读取元数据中...\n")
    
    try:
        #  files_metadata=True 允许我们获取到文件的真实大小
        info = api.model_info(repo_id, files_metadata=True)
    except Exception as e:
        print(f"❌ 查询失败，请检查仓库名是否正确或网络是否通畅。\n错误详情: {e}")
        return

    # 过滤出所有以 .gguf 结尾的文件
    gguf_files = []
    for f in info.siblings:
        if f.rfilename.endswith(".gguf"):
            size_gb = f.size / (1024**3) if f.size else 0
            gguf_files.append((f.rfilename, size_gb))

    if not gguf_files:
        print("⚠️ 哎呀，在这个仓库里没有找到任何 .gguf 文件。")
        return

    print("📦 找到以下 GGUF 文件：")
    print("-" * 50)
    for i, (fname, size) in enumerate(gguf_files):
        print(f"  [{i}] {fname}  (约 {size:.2f} GB)")
    print("-" * 50)

    choice = input("\n🎯 请输入要下载的文件编号 (输入 q 退出): ").strip()
    if choice.lower() == 'q' or not choice.isdigit():
        print("已取消下载。")
        return

    idx = int(choice)
    if 0 <= idx < len(gguf_files):
        target_file = gguf_files[idx][0]
        # 默认下载到你的大模型专用目录
        local_dir = os.path.expanduser("~/data/ai_server/models")
        
        print(f"\n🚀 目标锁定: {target_file}")
        print(f"📥 开始下载至: {local_dir}")
        print("⏳ 进度条加载中 (底层依赖 hf 核心，支持断点续传)...\n")
        
        try:
            hf_hub_download(
                repo_id=repo_id, 
                filename=target_file, 
                local_dir=local_dir,
                local_dir_use_symlinks=False # 直接下载实体文件，不搞软链接
            )
            print("\n✅ 下载圆满完成！你可以直接启动服务了。")
        except Exception as e:
            print(f"\n❌ 下载过程中断: {e}")
    else:
        print("❌ 编号无效，请重新运行。")

if __name__ == "__main__":
    main()
