"""
项目初始化脚本
首次运行时自动创建必要的目录和文件
"""
import os
import shutil
from pathlib import Path


def setup_project():
    """初始化项目结构"""
    print("=" * 60)
    print("🎮 无限流异世界恋爱 Visual Novel - 项目初始化")
    print("=" * 60)
    
    # 创建必要的目录
    directories = ["data", "cache", "assets"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}/")
        else:
            print(f"ℹ️  目录已存在: {directory}/")
    
    # 创建 .env 文件（如果不存在）
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print(f"✅ 创建配置文件: .env")
            print(f"⚠️  请编辑 .env 文件并填入你的 API 密钥！")
        else:
            print(f"❌ 未找到 env.example 文件")
    else:
        print(f"ℹ️  配置文件已存在: .env")
    
    print("\n" + "=" * 60)
    print("🎉 项目初始化完成！")
    print("=" * 60)
    print("\n📝 下一步操作：")
    print("1. 编辑 .env 文件，填入你的 SiliconFlow API 密钥")
    print("   获取密钥: https://cloud.siliconflow.cn")
    print("\n2. 安装依赖包:")
    print("   pip install -r requirements.txt")
    print("\n3. 运行应用:")
    print("   streamlit run app.py")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    setup_project()




