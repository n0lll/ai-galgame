"""
无限流异世界恋爱 Visual Novel - CLI 主入口
支持 Dry Run / Pre-flight Check 功能
"""
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入项目模块
from src.prompt_builder import PromptBuilder
from src.data_loader import load_config_from_yaml


def build_first_user_message() -> str:
    """
    构建第一个用户消息（用于 Dry Run 预览）
    
    Returns:
        第一个用户消息字符串
    """
    # 这里可以根据实际需求构建第一个用户消息
    # 示例：典型的 Visual Novel 生成请求
    return """请生成故事的第一个场景。
要求：
1. 介绍世界观和主要角色
2. 营造适当的氛围
3. 为后续剧情发展埋下伏笔"""


def perform_dry_run(config_path: Path) -> bool:
    """
    执行 Dry Run / Pre-flight Check
    
    此函数会：
    1. 加载配置和全局上下文
    2. 构建完整的 System Prompt 和第一个 User Message
    3. 验证内容不为空
    4. 保存到 debug_prompt_preview.txt
    5. 在控制台打印预览
    
    Args:
        config_path: config.yaml 文件路径
        
    Returns:
        True 如果检查通过，False 如果有警告
    """
    logger.info("=" * 70)
    logger.info("🔍 开始 Dry Run / Pre-flight Check")
    logger.info("=" * 70)
    
    # 1. 加载配置
    logger.info("📋 加载配置文件...")
    config = load_config_from_yaml(config_path)
    if not config:
        logger.warning("⚠️  配置文件为空或加载失败")
    
    # 2. 初始化 PromptBuilder（会自动加载全局上下文）
    logger.info("🔧 初始化 Prompt Builder...")
    try:
        prompt_builder = PromptBuilder(config=config, config_yaml_path=config_path)
    except Exception as e:
        logger.error(f"❌ Prompt Builder 初始化失败: {e}")
        return False
    
    # 3. 构建基础 System Prompt（使用默认模板）
    logger.info("📝 构建 System Prompt...")
    base_prompt = prompt_builder.get_base_system_prompt(task_type="story_generation")
    
    # 4. 构建完整的 System Prompt（包含全局上下文）
    full_system_prompt = prompt_builder.build_system_prompt(
        base_prompt=base_prompt,
        inject_global_context=True
    )
    
    # 5. 构建第一个 User Message
    first_user_message = build_first_user_message()
    
    # 6. 验证内容
    logger.info("✅ 验证提示词内容...")
    validation_passed = True
    
    if not full_system_prompt or not full_system_prompt.strip():
        logger.warning("⚠️  WARNING: System Prompt 为空！")
        validation_passed = False
    
    if not first_user_message or not first_user_message.strip():
        logger.warning("⚠️  WARNING: User Message 为空！")
        validation_passed = False
    
    # 检查全局上下文是否加载成功
    if prompt_builder._global_context_cache is None or not prompt_builder._global_context_cache.strip():
        logger.warning("⚠️  WARNING: 全局上下文未加载或为空！请检查 config.yaml 中的 global_context 配置。")
    
    # 7. 组装完整的提示词内容（用于预览）
    full_prompt_content = f"""=== SYSTEM PROMPT ===

{full_system_prompt}

=== FIRST USER MESSAGE ===

{first_user_message}

=== STATISTICS ===

System Prompt 长度: {len(full_system_prompt)} 字符
User Message 长度: {len(first_user_message)} 字符
总长度: {len(full_system_prompt) + len(first_user_message)} 字符
估算 Token 数（中文）: {int((len(full_system_prompt) + len(first_user_message)) * 0.7)} tokens
"""
    
    # 8. 保存到文件
    output_file = Path("debug_prompt_preview.txt")
    logger.info(f"💾 保存提示词预览到: {output_file}")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_prompt_content)
        logger.info(f"✅ 文件保存成功")
    except Exception as e:
        logger.error(f"❌ 保存文件失败: {e}")
        return False
    
    # 9. 控制台预览（前 500 字符和后 500 字符）
    logger.info("\n" + "=" * 70)
    logger.info("📄 提示词预览（前 500 字符）")
    logger.info("=" * 70)
    
    preview_start = full_system_prompt[:500]
    logger.info(preview_start)
    if len(full_system_prompt) > 500:
        logger.info(f"\n... (省略中间 {len(full_system_prompt) - 1000} 字符) ...")
    
    logger.info("\n" + "=" * 70)
    logger.info("📄 提示词预览（后 500 字符）")
    logger.info("=" * 70)
    
    preview_end = full_system_prompt[-500:]
    logger.info(preview_end)
    
    logger.info("\n" + "=" * 70)
    logger.info("📊 统计信息")
    logger.info("=" * 70)
    logger.info(f"System Prompt 长度: {len(full_system_prompt)} 字符")
    logger.info(f"User Message 长度: {len(first_user_message)} 字符")
    logger.info(f"总长度: {len(full_system_prompt) + len(first_user_message)} 字符")
    logger.info(f"估算 Token 数（中文）: {int((len(full_system_prompt) + len(first_user_message)) * 0.7)} tokens")
    
    if prompt_builder._global_context_cache:
        logger.info(f"全局上下文长度: {len(prompt_builder._global_context_cache)} 字符")
        logger.info(f"全局上下文 Token 估算: {int(len(prompt_builder._global_context_cache) * 0.7)} tokens")
    
    # 10. 完成消息
    logger.info("\n" + "=" * 70)
    if validation_passed:
        logger.info("✅ Dry Run 完成！检查通过，可以开始生成。")
    else:
        logger.info("⚠️  Dry Run 完成！发现警告，请检查上述信息。")
    logger.info(f"📄 完整提示词预览已保存到: {output_file.absolute()}")
    logger.info("=" * 70)
    
    # 重要提示：不调用 API，不修改 .progress 文件
    logger.info("💡 注意: Dry Run 模式不会调用 API，也不会修改任何状态文件（包括 .progress）")
    
    return validation_passed


def main():
    """主函数 - CLI 入口点"""
    parser = argparse.ArgumentParser(
        description="无限流异世界恋爱 Visual Novel - CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 正常模式（生成故事）
  python main.py
  
  # Dry Run 模式（预览提示词，不调用 API）
  python main.py --dry-run
  
  # 使用自定义配置文件
  python main.py --dry-run --config custom_config.yaml
        """
    )
    
    parser.add_argument(
        "--dry-run",
        "--inspect",
        dest="dry_run",
        action="store_true",
        help="执行 Dry Run / Pre-flight Check（不调用 API，不修改状态文件）"
    )
    
    parser.add_argument(
        "--config",
        dest="config_path",
        type=str,
        default="config.yaml",
        help="配置文件路径（默认: config.yaml）"
    )
    
    args = parser.parse_args()
    
    config_path = Path(args.config_path)
    
    # 检查配置文件是否存在
    if not config_path.exists():
        logger.error(f"❌ 配置文件不存在: {config_path}")
        logger.info("💡 请确保配置文件存在，或使用 --config 指定路径")
        return 1
    
    # 根据模式执行
    if args.dry_run:
        # Dry Run 模式
        success = perform_dry_run(config_path)
        return 0 if success else 1
    else:
        # 正常模式（生成故事）
        logger.info("🚀 正常模式：开始故事生成...")
        logger.info("💡 提示：使用 --dry-run 可以预览提示词而不调用 API")
        logger.warning("⚠️  正常模式尚未实现，请先使用 --dry-run 进行预检查")
        return 0


if __name__ == "__main__":
    exit(main())

