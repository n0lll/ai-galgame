# 🎮 无限流异世界恋爱 Visual Novel

一款基于 AI 驱动的无限流异世界恋爱 Visual Novel 游戏。

## ✨ 特色功能

- 🎨 **AI 驱动的动态剧情生成**: 使用 DeepSeek V3 生成独特的故事情节
- 🖼️ **实时角色立绘生成**: 通过 Flux 模型生成精美的角色图像
- 💾 **多存档系统**: 支持多个存档槽位，随时保存和加载进度
- 🎯 **个性化角色互动**: 角色拥有动态属性，互动影响剧情走向
- 🌟 **风格化图像生成**: 基于 Style-RAG 的风格一致性图像生成

## 🛠️ 技术栈

- **Python 3.10+**: 核心开发语言
- **Streamlit**: Web UI 框架
- **Pydantic**: 数据验证和建模
- **SQLite**: 游戏存档数据库
- **LanceDB**: 向量数据库，用于 Style-RAG
- **OpenAI SDK**: API 调用（兼容 SiliconFlow）

## 📦 安装步骤

### 1. 克隆项目

```bash
git clone <repository_url>
cd ai-galgame
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.template` 到 `.env` 并填入你的 API 密钥：

```bash
cp .env.template .env
```

编辑 `.env` 文件，设置你的 SiliconFlow API 密钥：

```env
OPENAI_API_KEY=your_api_key_here
```

**获取 API 密钥**: [SiliconFlow Cloud](https://cloud.siliconflow.cn)

### 5. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址: http://localhost:8501

## 📁 项目结构

```
ai-galgame/
├── app.py                 # Streamlit 应用入口
├── src/
│   ├── __init__.py
│   ├── models.py          # 核心数据模型（Pydantic）
│   ├── database.py        # 数据库操作（SQLite + LanceDB）
│   └── config.py          # 配置管理
├── data/                  # 数据存储目录（自动创建）
│   ├── saves.db          # SQLite 存档数据库
│   └── lancedb/          # LanceDB 向量数据库
├── cache/                 # 缓存目录（自动创建）
├── assets/                # 资源文件目录（自动创建）
├── .env                   # 环境变量配置
├── .env.template          # 环境变量模板
├── .gitignore            # Git 忽略文件
├── requirements.txt       # Python 依赖
└── README.md             # 项目说明文档
```

## 🎯 核心模块说明

### models.py - 数据模型

- **Character**: 角色数据模型
  - `visual_traits`: 视觉特征（发色、瞳色、服装等）
  - `base_img_ref`: PuLID 参考图 URL
  - `stats`: 动态属性（好感度、信任度等）

- **GameState**: 游戏状态模型
  - `turn_count`: 回合计数
  - `current_location`: 当前位置
  - `active_characters`: 活跃角色列表
  - `inventory`: 物品背包
  - `flags`: 剧情标志位

- **GameConfig**: 游戏配置模型
  - `visual_backend`: 视觉生成后端（siliconflow/local_pony）
  - `difficulty`: 游戏难度
  - `style_tags`: 风格标签

### database.py - 数据库操作

- **SQLiteDatabase**: SQLite 数据库管理
  - `save_game()`: 保存游戏状态
  - `load_game()`: 加载游戏状态
  - `get_all_saves()`: 获取所有存档
  - `delete_save()`: 删除存档

- **LanceDBDatabase**: LanceDB 向量数据库管理
  - `add_chunk()`: 添加文本片段（占位）
  - `search_similar()`: 搜索相似文本（占位）

### config.py - 配置管理

- **APIConfig**: API 配置
  - OpenAI 兼容 API 设置
  - DeepSeek 和 Flux 模型配置

- **AppConfig**: 应用配置
  - 路径配置
  - 游戏配置
  - 图像生成配置

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | API 密钥（必填） | - |
| `OPENAI_BASE_URL` | API 基础 URL | `https://api.siliconflow.cn/v1` |
| `DEEPSEEK_MODEL` | DeepSeek 模型 | `deepseek-ai/DeepSeek-V3` |
| `FLUX_MODEL` | Flux 图像模型 | `black-forest-labs/FLUX.1-schnell` |
| `DEBUG_MODE` | 调试模式 | `false` |

完整配置项请参考 `.env.template` 文件。

## 🚀 开发路线图

- [x] 项目骨架搭建
- [ ] 剧情生成引擎
- [ ] 角色立绘生成
- [ ] Style-RAG 实现
- [ ] 存档系统完善
- [ ] UI 美化和动画
- [ ] 音效和背景音乐
- [ ] 多结局系统

## 📝 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**© 2025 无限流异世界恋爱 Visual Novel | Powered by AI**




