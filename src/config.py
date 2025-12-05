"""
环境变量与配置加载
管理 API 密钥和应用程序配置
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# 加载 .env 文件
env_path = Path(".env")
if env_path.exists():
    load_dotenv(env_path)
    print("[配置] 成功加载 .env 文件")
else:
    print("[配置] 未找到 .env 文件，使用默认配置")


class APIConfig(BaseModel):
    """API 配置模型"""
    
    # OpenAI 兼容 API 配置（用于 SiliconFlow）
    api_key: str = Field(
        default="",
        description="API 密钥"
    )
    base_url: str = Field(
        default="https://api.siliconflow.cn/v1",
        description="API 基础 URL"
    )
    
    # DeepSeek 模型配置
    deepseek_model: str = Field(
        default="deepseek-ai/DeepSeek-V3",
        description="DeepSeek 对话模型"
    )
    
    # Flux 图像生成模型配置
    flux_model: str = Field(
        default="black-forest-labs/FLUX.1-schnell",
        description="Flux 图像生成模型"
    )
    
    # 请求超时设置
    timeout: int = Field(
        default=60,
        description="API 请求超时时间（秒）"
    )
    
    # 最大重试次数
    max_retries: int = Field(
        default=3,
        description="API 请求最大重试次数"
    )


class AppConfig(BaseModel):
    """应用程序配置模型"""
    
    # 应用基本信息
    app_name: str = Field(
        default="无限流异世界恋爱 Visual Novel",
        description="应用程序名称"
    )
    version: str = Field(
        default="0.1.0",
        description="版本号"
    )
    
    # 数据存储路径
    data_dir: Path = Field(
        default=Path("data"),
        description="数据存储目录"
    )
    cache_dir: Path = Field(
        default=Path("cache"),
        description="缓存目录"
    )
    assets_dir: Path = Field(
        default=Path("assets"),
        description="资源文件目录"
    )
    
    # 游戏配置
    max_save_slots: int = Field(
        default=10,
        description="最大存档槽位数"
    )
    auto_save_interval: int = Field(
        default=5,
        description="自动保存间隔（回合数）"
    )
    
    # 图像生成配置
    image_width: int = Field(
        default=512,
        description="生成图像宽度"
    )
    image_height: int = Field(
        default=768,
        description="生成图像高度"
    )
    image_cache_enabled: bool = Field(
        default=True,
        description="是否启用图像缓存"
    )
    
    # 调试模式
    debug_mode: bool = Field(
        default=False,
        description="调试模式"
    )


class Config:
    """全局配置管理类"""
    
    def __init__(self):
        # 初始化 API 配置
        self.api = APIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.siliconflow.cn/v1"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3"),
            flux_model=os.getenv("FLUX_MODEL", "black-forest-labs/FLUX.1-schnell"),
            timeout=int(os.getenv("API_TIMEOUT", "60")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3"))
        )
        
        # 初始化应用配置
        self.app = AppConfig(
            app_name=os.getenv("APP_NAME", "无限流异世界恋爱 Visual Novel"),
            version=os.getenv("APP_VERSION", "0.1.0"),
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            cache_dir=Path(os.getenv("CACHE_DIR", "cache")),
            assets_dir=Path(os.getenv("ASSETS_DIR", "assets")),
            max_save_slots=int(os.getenv("MAX_SAVE_SLOTS", "10")),
            auto_save_interval=int(os.getenv("AUTO_SAVE_INTERVAL", "5")),
            image_width=int(os.getenv("IMAGE_WIDTH", "512")),
            image_height=int(os.getenv("IMAGE_HEIGHT", "768")),
            image_cache_enabled=os.getenv("IMAGE_CACHE_ENABLED", "true").lower() == "true",
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
        )
        
        # 确保必要的目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        for directory in [self.app.data_dir, self.app.cache_dir, self.app.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """
        验证配置是否完整
        
        Returns:
            bool: 配置是否有效
        """
        errors = []
        
        # 检查 API 密钥
        if not self.api.api_key:
            errors.append("缺少 API 密钥 (OPENAI_API_KEY)")
        
        # 检查必要的目录权限
        for dir_name, directory in [
            ("数据目录", self.app.data_dir),
            ("缓存目录", self.app.cache_dir),
            ("资源目录", self.app.assets_dir)
        ]:
            if not directory.exists():
                errors.append(f"{dir_name} 不存在: {directory}")
            elif not os.access(directory, os.W_OK):
                errors.append(f"{dir_name} 无写入权限: {directory}")
        
        if errors:
            print("[配置] 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("[配置] 配置验证成功")
        return True
    
    def print_info(self):
        """打印配置信息（调试用）"""
        print("=" * 50)
        print(f"应用名称: {self.app.app_name}")
        print(f"版本: {self.app.version}")
        print(f"API 基础 URL: {self.api.base_url}")
        print(f"DeepSeek 模型: {self.api.deepseek_model}")
        print(f"Flux 模型: {self.api.flux_model}")
        print(f"数据目录: {self.app.data_dir}")
        print(f"缓存目录: {self.app.cache_dir}")
        print(f"资源目录: {self.app.assets_dir}")
        print(f"调试模式: {self.app.debug_mode}")
        print(f"API 密钥已设置: {'是' if self.api.api_key else '否'}")
        print("=" * 50)


# 创建全局配置实例
config = Config()


# 便捷访问函数
def get_config() -> Config:
    """获取全局配置实例"""
    return config


def get_api_config() -> APIConfig:
    """获取 API 配置"""
    return config.api


def get_app_config() -> AppConfig:
    """获取应用配置"""
    return config.app




