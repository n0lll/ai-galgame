"""
无限流异世界恋爱 Visual Novel
Streamlit 应用程序入口
"""
import streamlit as st
from pathlib import Path

# 导入配置
from src.config import config


def main():
    """主应用程序函数"""
    
    # 页面配置
    st.set_page_config(
        page_title=config.app.app_name,
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 主标题
    st.title(f"🎮 {config.app.app_name}")
    st.markdown(f"**版本**: {config.app.version}")
    
    # 分隔线
    st.divider()
    
    # Hello World 占位内容
    st.header("✨ 欢迎来到异世界！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📖 游戏简介")
        st.markdown("""
        这是一款结合了**无限流**元素的**异世界恋爱 Visual Novel**游戏。
        
        **特色功能：**
        - 🎨 AI 驱动的动态剧情生成
        - 🖼️ 实时角色立绘生成
        - 💾 多存档系统
        - 🎯 个性化角色互动
        - 🌟 风格化图像生成 (Style-RAG)
        """)
    
    with col2:
        st.subheader("⚙️ 系统状态")
        
        # 检查配置
        is_valid = config.validate()
        
        if is_valid:
            st.success("✅ 系统配置正常")
        else:
            st.error("❌ 系统配置存在问题，请检查 .env 文件")
        
        # 显示配置信息
        st.markdown(f"""
        **API 基础 URL**: `{config.api.base_url}`  
        **DeepSeek 模型**: `{config.api.deepseek_model}`  
        **Flux 模型**: `{config.api.flux_model}`  
        **API 密钥**: {'✅ 已设置' if config.api.api_key else '❌ 未设置'}
        """)
    
    st.divider()
    
    # 快速操作按钮
    st.subheader("🎮 快速开始")
    
    button_col1, button_col2, button_col3 = st.columns(3)
    
    with button_col1:
        if st.button("🆕 开始新游戏", use_container_width=True, type="primary"):
            st.info("🚧 此功能正在开发中...")
    
    with button_col2:
        if st.button("📂 读取存档", use_container_width=True):
            st.info("🚧 此功能正在开发中...")
    
    with button_col3:
        if st.button("⚙️ 设置", use_container_width=True):
            st.info("🚧 此功能正在开发中...")
    
    st.divider()
    
    # 侧边栏
    with st.sidebar:
        st.header("📊 调试信息")
        
        if config.app.debug_mode:
            st.warning("🔧 调试模式已启用")
            
            with st.expander("查看完整配置"):
                st.json({
                    "app": {
                        "name": config.app.app_name,
                        "version": config.app.version,
                        "data_dir": str(config.app.data_dir),
                        "cache_dir": str(config.app.cache_dir),
                        "assets_dir": str(config.app.assets_dir),
                    },
                    "api": {
                        "base_url": config.api.base_url,
                        "deepseek_model": config.api.deepseek_model,
                        "flux_model": config.api.flux_model,
                        "has_api_key": bool(config.api.api_key)
                    }
                })
        else:
            st.info("💡 在 .env 中设置 DEBUG_MODE=true 以启用调试模式")
        
        st.divider()
        
        st.markdown("""
        ### 📚 开发信息
        
        **技术栈:**
        - Python 3.10+
        - Streamlit
        - Pydantic
        - SQLite
        - LanceDB
        - OpenAI SDK
        
        **当前状态:**  
        项目骨架已完成 ✅
        """)
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "© 2025 无限流异世界恋爱 Visual Novel | Powered by AI"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()




