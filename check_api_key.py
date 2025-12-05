"""
API Key 配置检查脚本
快速验证您的 API Key 是否配置正确
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def check_api_key():
    """检查 API Key 配置"""
    print("=" * 70)
    print("🔍 API Key 配置检查")
    print("=" * 70)
    
    # 加载 .env 文件
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ 找到 .env 文件")
    else:
        print("⚠️  .env 文件不存在")
        print("   提示: 可以从 env.example 复制一个模板")
    
    # 检查环境变量
    print("\n[检查环境变量]")
    
    siliconflow_key = os.getenv("SILICONFLOW_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if siliconflow_key:
        print(f"✅ SILICONFLOW_API_KEY: 已设置")
        print(f"   长度: {len(siliconflow_key)} 字符")
        print(f"   前10个字符: {siliconflow_key[:10]}...")
        if siliconflow_key == "your_api_key_here" or not siliconflow_key.startswith("sk-"):
            print("   ⚠️  警告: 看起来还是默认值或格式不正确")
            return False
        api_key = siliconflow_key
    elif openai_key:
        print(f"✅ OPENAI_API_KEY: 已设置")
        print(f"   长度: {len(openai_key)} 字符")
        print(f"   前10个字符: {openai_key[:10]}...")
        if openai_key == "your_api_key_here" or not openai_key.startswith("sk-"):
            print("   ⚠️  警告: 看起来还是默认值或格式不正确")
            return False
        api_key = openai_key
    else:
        print("❌ 未找到 API Key")
        print("   请设置 SILICONFLOW_API_KEY 或 OPENAI_API_KEY")
        print("\n💡 配置方法:")
        print("   1. 编辑 .env 文件")
        print("   2. 设置: SILICONFLOW_API_KEY=sk-your-key-here")
        return False
    
    # 验证格式
    print("\n[验证格式]")
    if api_key.startswith("sk-"):
        print("✅ API Key 格式正确（以 sk- 开头）")
    else:
        print("⚠️  API Key 格式可能不正确（通常以 sk- 开头）")
    
    if len(api_key) > 20:
        print(f"✅ API Key 长度合理（{len(api_key)} 字符）")
    else:
        print(f"⚠️  API Key 可能太短（{len(api_key)} 字符）")
    
    # 测试 ETL Pipeline 读取
    print("\n[测试 ETL Pipeline 读取]")
    try:
        from src.etl_pipeline import get_api_key
        test_key = get_api_key()
        if test_key == api_key:
            print("✅ ETL Pipeline 可以正常读取 API Key")
        else:
            print("⚠️  ETL Pipeline 读取的 Key 与直接读取的不一致")
            return False
    except Exception as e:
        print(f"❌ ETL Pipeline 读取失败: {e}")
        return False
    
    # 测试应用配置读取
    print("\n[测试应用配置读取]")
    try:
        from src.config import get_api_config
        api_config = get_api_config()
        if api_config.api_key:
            print("✅ 应用配置可以正常读取 API Key")
        else:
            print("⚠️  应用配置中 API Key 为空")
    except Exception as e:
        print(f"⚠️  应用配置读取测试失败: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 检查结果")
    print("=" * 70)
    print("✅ API Key 配置正确！")
    print("\n💡 下一步:")
    print("   可以运行: python src/etl_pipeline.py")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = check_api_key()
    if not success:
        print("\n❌ 配置检查失败，请按照提示修复问题")
        exit(1)
    else:
        print("\n🎉 所有检查通过！")



