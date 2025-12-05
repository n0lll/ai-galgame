"""
全局上下文数据加载模块
用于安全地加载和注入静态知识库（World Setting 和 Romance Guide）
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 配置日志
logger = logging.getLogger(__name__)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    安全地加载 JSON 文件
    
    Args:
        file_path: JSON 文件路径
        
    Returns:
        解析后的字典，如果失败则返回 None
    """
    try:
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"成功加载 JSON 文件: {file_path}")
            return data
    
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 解析失败 ({file_path}): {e}")
        return None
    
    except Exception as e:
        logger.warning(f"加载文件失败 ({file_path}): {e}")
        return None


def load_global_context(config: Dict[str, Any]) -> str:
    """
    加载全局上下文（World Setting 和 Romance Guide）
    
    此函数从配置中读取文件路径，安全地加载 JSON 数据，
    并格式化为可用于 LLM Prompt 的字符串。
    
    特性：
    - 防御性编程：优雅处理缺失文件和格式错误的 JSON
    - 向后兼容：如果配置中缺少 global_context 或 enable 为 False，返回空字符串
    - 字符编码：使用 ensure_ascii=False 保留中文字符
    
    Args:
        config: 配置字典，应包含 global_context 配置段
        
    Returns:
        格式化后的全局上下文字符串，如果禁用或失败则返回空字符串
    """
    # 安全获取 global_context 配置（如果不存在则返回默认值）
    global_context_config = config.get("global_context", {})
    
    # 检查是否启用
    if not global_context_config.get("enable", False):
        logger.debug("全局上下文注入功能未启用")
        return ""
    
    # 获取文件路径（使用相对路径，从项目根目录开始）
    world_setting_path = global_context_config.get("world_setting_path", "./data/world_setting.json")
    romance_setting_path = global_context_config.get("romance_setting_path", "./data/romance_setting.json")
    
    # 转换为 Path 对象（处理相对路径）
    project_root = Path(__file__).parent.parent  # src 的父目录 = 项目根目录
    world_path = project_root / Path(world_setting_path)
    romance_path = project_root / Path(romance_setting_path)
    
    # 加载 JSON 文件（防御性：缺失或格式错误时返回 None）
    world_data = load_json_file(world_path)
    romance_data = load_json_file(romance_path)
    
    # 如果两个文件都加载失败，返回空字符串
    if world_data is None and romance_data is None:
        logger.warning("全局上下文文件加载失败，将使用空上下文")
        return ""
    
    # 构建格式化字符串（使用 string.Template 避免 f-string 与 JSON {} 冲突）
    from string import Template
    
    # 将 JSON 数据序列化为字符串（保留中文字符）
    world_json_str = ""
    if world_data is not None:
        try:
            world_json_str = json.dumps(world_data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"序列化 World Setting 失败: {e}")
            world_json_str = ""
    
    romance_json_str = ""
    if romance_data is not None:
        try:
            romance_json_str = json.dumps(romance_data, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"序列化 Romance Guide 失败: {e}")
            romance_json_str = ""
    
    # 使用 Template 安全地插入 JSON 字符串（避免 {} 冲突）
    template = Template("""[Global Context / World Bible]

The following JSON data contains the immutable laws of the world and relationship guidelines. You must strictly adhere to these settings throughout the generation.

<World_Setting>
${world_setting}
</World_Setting>

<Romance_Guide>
${romance_guide}
</Romance_Guide>
""")
    
    # 如果没有数据，插入空占位符或提示
    if not world_json_str:
        world_json_str = "{}  # 未加载或加载失败"
    if not romance_json_str:
        romance_json_str = "{}  # 未加载或加载失败"
    
    # 替换模板变量
    context_string = template.substitute(
        world_setting=world_json_str,
        romance_guide=romance_json_str
    )
    
    logger.info(f"全局上下文加载完成 (World Setting: {len(world_json_str)} 字符, Romance Guide: {len(romance_json_str)} 字符)")
    return context_string


def load_config_from_yaml(yaml_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    从 YAML 文件加载配置（可选辅助函数）
    
    Args:
        yaml_path: YAML 配置文件路径，如果为 None 则使用默认路径
        
    Returns:
        配置字典，如果文件不存在或解析失败则返回空字典
    """
    if yaml_path is None:
        yaml_path = Path(__file__).parent.parent / "config.yaml"
    
    try:
        # 尝试导入 yaml 库（如果未安装则返回空字典）
        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML 未安装，无法读取 config.yaml。请安装: pip install pyyaml")
            return {}
        
        if not yaml_path.exists():
            logger.debug(f"配置文件不存在: {yaml_path}，使用空配置")
            return {}
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            logger.debug(f"成功加载配置文件: {yaml_path}")
            return config
    
    except Exception as e:
        logger.warning(f"加载 YAML 配置失败: {e}，使用空配置")
        return {}

