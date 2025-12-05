"""
Prompt 构建模块
用于构建和组装 System Prompt，支持全局上下文注入
"""
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from .data_loader import load_global_context, load_config_from_yaml

# 配置日志
logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Prompt 构建器
    用于组装 System Prompt，支持全局上下文注入
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_yaml_path: Optional[Path] = None):
        """
        初始化 Prompt 构建器
        
        Args:
            config: 配置字典（如果提供，将直接使用）
            config_yaml_path: config.yaml 文件路径（如果提供，将从此文件加载配置）
        """
        if config is not None:
            self.config = config
        elif config_yaml_path is not None:
            self.config = load_config_from_yaml(config_yaml_path)
        else:
            # 尝试从默认位置加载
            self.config = load_config_from_yaml()
        
        # 预加载全局上下文（如果启用）
        self._global_context_cache: Optional[str] = None
        self._load_global_context()
    
    def _load_global_context(self):
        """预加载全局上下文到缓存"""
        try:
            self._global_context_cache = load_global_context(self.config)
            if self._global_context_cache:
                logger.info("全局上下文已加载并缓存")
        except Exception as e:
            logger.warning(f"加载全局上下文失败: {e}")
            self._global_context_cache = None
    
    def build_system_prompt(
        self,
        base_prompt: str,
        inject_global_context: bool = True
    ) -> str:
        """
        构建完整的 System Prompt，可选择性地注入全局上下文
        
        此方法会在 base_prompt 之后追加全局上下文（如果启用）。
        全局上下文来自 config.yaml 中配置的 World Setting 和 Romance Guide。
        
        关键特性：
        - 向后兼容：如果全局上下文未启用或加载失败，只返回 base_prompt
        - 防御性：即使注入失败也不会中断程序
        - 安全格式化：使用字符串拼接而非 f-string，避免 JSON {} 冲突
        
        Args:
            base_prompt: 基础 System Prompt（核心指令）
            inject_global_context: 是否注入全局上下文（默认 True）
            
        Returns:
            完整的 System Prompt 字符串
        """
        if not inject_global_context or not self._global_context_cache:
            return base_prompt
        
        # 使用字符串拼接而非 f-string，避免 JSON 中的 {} 与 f-string 冲突
        # 将全局上下文追加到基础 Prompt 之后
        full_prompt = base_prompt + "\n\n" + self._global_context_cache
        
        logger.debug(f"System Prompt 构建完成 (基础: {len(base_prompt)} 字符, 全局上下文: {len(self._global_context_cache)} 字符)")
        return full_prompt
    
    def get_base_system_prompt(self, task_type: str = "story_generation") -> str:
        """
        获取基础 System Prompt 模板
        
        Args:
            task_type: 任务类型（"story_generation", "dialogue", "scene_description" 等）
            
        Returns:
            基础 System Prompt 字符串
        """
        base_prompts = {
            "story_generation": """你是一个专业的 Visual Novel 剧情生成器。
你的任务是生成引人入胜的异世界恋爱故事。

要求：
1. 保持角色性格一致性
2. 遵循世界观的设定和规则
3. 营造浪漫的氛围
4. 推进剧情发展""",
            
            "dialogue": """你是一个专业的角色对话生成器。
你的任务是基于角色设定和当前情境生成符合角色性格的对话。

要求：
1. 符合角色的说话风格
2. 反映角色的当前情感状态
3. 推动剧情发展
4. 保持对话自然流畅""",
            
            "scene_description": """你是一个专业的场景描述生成器。
你的任务是基于世界观设定和当前剧情状态生成生动的场景描述。

要求：
1. 符合世界观的设定
2. 营造适当的氛围
3. 与剧情发展协调
4. 包含丰富的感官细节"""
        }
        
        return base_prompts.get(task_type, base_prompts["story_generation"])
    
    def build_full_system_prompt(
        self,
        task_type: str = "story_generation",
        custom_base: Optional[str] = None,
        inject_global_context: bool = True
    ) -> str:
        """
        构建完整的 System Prompt（便捷方法）
        
        Args:
            task_type: 任务类型（用于选择基础模板）
            custom_base: 自定义基础 Prompt（如果提供，将覆盖 task_type）
            inject_global_context: 是否注入全局上下文
            
        Returns:
            完整的 System Prompt 字符串
        """
        base_prompt = custom_base if custom_base is not None else self.get_base_system_prompt(task_type)
        return self.build_system_prompt(base_prompt, inject_global_context=inject_global_context)


def build_system_prompt_with_context(
    base_prompt: str,
    config: Optional[Dict[str, Any]] = None,
    config_yaml_path: Optional[Path] = None
) -> str:
    """
    便捷函数：快速构建带全局上下文的 System Prompt
    
    这是一个静态函数，用于在不创建 PromptBuilder 实例的情况下快速使用。
    
    Args:
        base_prompt: 基础 System Prompt
        config: 配置字典（可选）
        config_yaml_path: config.yaml 文件路径（可选）
        
    Returns:
        完整的 System Prompt 字符串
    """
    builder = PromptBuilder(config=config, config_yaml_path=config_yaml_path)
    return builder.build_system_prompt(base_prompt)

