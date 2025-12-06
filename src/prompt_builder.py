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

【语言要求】
- **所有输出必须使用简体中文**
- 对话、叙述、描述均使用中文
- 保持中文表达的流畅性和地道性
- 禁止在输出中使用英文单词（除非是特定品牌名或无法翻译的专有名词）

【专有名词处理规则】
- 如果世界观设定中包含英文专有名词、术语或概念，请自动将其翻译为地道的中文奇幻小说术语
- 翻译要求：
  * 符合中文奇幻小说的命名习惯（如："魔法师"而非"Magician"，"灵脉"而非"Mana Source"）
  * 保持术语的一致性（同一概念在全文中必须使用同一译名，不能出现前后不一致的情况）
  * 优先使用经典中文奇幻术语（如："元素"、"法阵"、"魂体"、"灵力"等）
  * 人名、地名等专有名词要保持奇幻风格，符合中文语境
  * 军事、政治、经济等术语也要翻译为符合世界观的中文表达
- 翻译示例：
  * "Hero class units" → "英雄级单位" 或 "传奇战士"
  * "Entity Assimilation" → "实体融合" 或 "魂体同化"
  * "Agricultural collapse" → "农业崩坏" 或 "粮荒时代"
  * "Extreme caloric deficit" → "极端饥荒" 或 "食物匮乏"
  * "Machiavellian decay" → "权谋崩坏" 或 "政治腐败"
  * "Supernatural power" → "超自然力量" 或 "灵力"
- **一致性检查**：在生成过程中，如果使用了某个术语的翻译，后续所有提及同一概念的地方都必须使用相同的翻译

要求：
1. 保持角色性格一致性
2. 遵循世界观的设定和规则（参考下方全局上下文，但需将英文术语翻译为中文）
3. 营造浪漫的氛围
4. 推进剧情发展
5. **确保所有生成内容均为简体中文**""",
            
            "dialogue": """你是一个专业的角色对话生成器。
你的任务是基于角色设定和当前情境生成符合角色性格的对话。

【语言要求】
- **所有对话必须使用简体中文**
- 保持中文表达的流畅性和地道性
- 禁止在对话中使用英文单词

【专有名词处理规则】
- 如果世界观设定中包含英文专有名词，请自动将其翻译为地道的中文奇幻小说术语
- 保持术语翻译的一致性（同一概念在全文中使用同一译名）
- 优先使用符合中文奇幻小说习惯的表达方式

要求：
1. 符合角色的说话风格
2. 反映角色的当前情感状态
3. 推动剧情发展
4. 保持对话自然流畅
5. **确保所有对话均为简体中文**""",
            
            "scene_description": """你是一个专业的场景描述生成器。
你的任务是基于世界观设定和当前剧情状态生成生动的场景描述。

【语言要求】
- **所有描述必须使用简体中文**
- 保持中文表达的流畅性和地道性
- 禁止在描述中使用英文单词

【专有名词处理规则】
- 如果世界观设定中包含英文专有名词，请自动将其翻译为地道的中文奇幻小说术语
- 保持术语翻译的一致性（同一概念在全文中使用同一译名）
- 优先使用符合中文奇幻小说习惯的表达方式

要求：
1. 符合世界观的设定
2. 营造适当的氛围
3. 与剧情发展协调
4. 包含丰富的感官细节
5. **确保所有描述均为简体中文**"""
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

