"""
故事生成器示例
展示如何集成全局上下文注入功能到实际的故事生成逻辑中
"""
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from .prompt_builder import PromptBuilder, build_system_prompt_with_context
from .data_loader import load_config_from_yaml

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StoryGenerator:
    """
    故事生成器
    演示如何在实际生成逻辑中使用全局上下文注入
    """
    
    def __init__(self, config_yaml_path: Optional[Path] = None):
        """
        初始化故事生成器
        
        Args:
            config_yaml_path: config.yaml 文件路径（可选）
        """
        # 加载配置
        self.config = load_config_from_yaml(config_yaml_path)
        
        # 初始化 Prompt 构建器
        self.prompt_builder = PromptBuilder(config=self.config, config_yaml_path=config_yaml_path)
    
    def generate_story(
        self,
        context: Dict[str, Any],
        user_message: str,
        use_global_context: bool = True
    ) -> str:
        """
        生成故事内容
        
        此方法演示了如何在实际生成逻辑中使用全局上下文：
        1. 构建基础 System Prompt
        2. 自动注入全局上下文（如果启用）
        3. 组装完整的消息列表
        
        Args:
            context: 当前故事上下文（当前场景、角色、剧情进度等）
            user_message: 用户输入或当前回合的指令
            use_global_context: 是否使用全局上下文注入（默认 True）
            
        Returns:
            生成的故事内容
        """
        # 构建基础 System Prompt（包含当前故事状态）
        base_prompt = self._build_base_prompt(context)
        
        # 使用 PromptBuilder 注入全局上下文
        full_system_prompt = self.prompt_builder.build_system_prompt(
            base_prompt=base_prompt,
            inject_global_context=use_global_context
        )
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        logger.info(f"System Prompt 长度: {len(full_system_prompt)} 字符")
        logger.debug(f"是否包含全局上下文: {use_global_context and self.prompt_builder._global_context_cache is not None}")
        
        # 这里应该调用 LLM API 生成内容
        # 示例：return await self._call_llm_api(messages)
        
        return "[故事生成逻辑应在这里调用 LLM API]"
    
    def _build_base_prompt(self, context: Dict[str, Any]) -> str:
        """
        构建基础 System Prompt（不包含全局上下文）
        
        这个方法构建的是动态部分，包含当前游戏状态、角色信息等。
        全局上下文（World Setting 和 Romance Guide）会由 PromptBuilder 自动追加。
        
        Args:
            context: 当前故事上下文
            
        Returns:
            基础 System Prompt 字符串
        """
        # 使用字符串拼接，避免与 JSON {} 冲突
        prompt_parts = [
            "你是一个专业的 Visual Novel 剧情生成器。",
            "你的任务是生成引人入胜的异世界恋爱故事。",
            "",
            "当前故事状态：",
            f"- 当前场景: {context.get('current_location', '未知')}",
            f"- 回合数: {context.get('turn_count', 0)}",
            f"- 剧情阶段: {context.get('current_phase', 'intro')}",
            "",
            "要求：",
            "1. 保持角色性格一致性",
            "2. 遵循世界观的设定和规则（参考下方全局上下文）",
            "3. 营造浪漫的氛围",
            "4. 推进剧情发展"
        ]
        
        return "\n".join(prompt_parts)


def example_usage():
    """
    使用示例：演示如何在实际代码中集成全局上下文注入
    """
    # 方法 1: 使用 PromptBuilder 类（推荐，适合需要多次构建的场景）
    builder = PromptBuilder(config_yaml_path=Path("config.yaml"))
    
    base_prompt = "你是一个专业的故事生成器..."
    full_prompt = builder.build_system_prompt(base_prompt, inject_global_context=True)
    
    print("=== 方法 1: 使用 PromptBuilder 类 ===")
    print(f"完整 Prompt 长度: {len(full_prompt)} 字符")
    
    # 方法 2: 使用便捷函数（适合一次性使用）
    full_prompt_2 = build_system_prompt_with_context(
        base_prompt="你是一个专业的故事生成器...",
        config_yaml_path=Path("config.yaml")
    )
    
    print("\n=== 方法 2: 使用便捷函数 ===")
    print(f"完整 Prompt 长度: {len(full_prompt_2)} 字符")
    
    # 方法 3: 在 StoryGenerator 中使用（完整集成示例）
    generator = StoryGenerator(config_yaml_path=Path("config.yaml"))
    
    context = {
        "current_location": "咖啡厅",
        "turn_count": 10,
        "current_phase": "rising_action"
    }
    
    story = generator.generate_story(
        context=context,
        user_message="生成下一个场景",
        use_global_context=True
    )
    
    print("\n=== 方法 3: 在 StoryGenerator 中使用 ===")
    print(f"生成结果: {story}")


if __name__ == "__main__":
    example_usage()

