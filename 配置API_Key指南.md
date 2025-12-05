# 🔑 硅基流动 API Key 配置指南

## 📋 配置步骤

### 方法 1：使用 .env 文件（推荐）✨

这是最简单和推荐的方法。

#### 步骤 1: 获取 API Key

1. 访问硅基流动控制台：https://cloud.siliconflow.cn
2. 登录您的账户
3. 进入「API 密钥」页面
4. 创建新的 API Key 或复制已有的 Key

#### 步骤 2: 配置 .env 文件

项目根目录应该已经有一个 `.env` 文件（如果没有，可以从 `env.example` 复制）。

编辑 `.env` 文件，找到这一行：

```env
OPENAI_API_KEY=your_api_key_here
```

将其替换为您的真实 API Key：

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**或者使用专用的环境变量名：**

```env
SILICONFLOW_API_KEY=sk-your-actual-api-key-here
```

**两种方式都可以，程序会自动识别！**

#### 步骤 3: 验证配置

运行测试命令：

```bash
python -c "from src.etl_pipeline import get_api_key; print('✅ API Key 配置成功:', get_api_key()[:10] + '...')"
```

或者运行测试脚本：

```bash
python test_etl_pipeline.py
```

---

### 方法 2：使用系统环境变量

如果您不想使用 .env 文件，可以设置系统环境变量。

#### Windows (PowerShell)

**临时设置（仅当前会话有效）：**
```powershell
$env:SILICONFLOW_API_KEY="sk-your-api-key-here"
# 或
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**永久设置（需要管理员权限）：**
```powershell
[System.Environment]::SetEnvironmentVariable('SILICONFLOW_API_KEY', 'sk-your-api-key-here', 'User')
```

设置后需要**重启终端**或 IDE。

#### Windows (CMD)

**临时设置：**
```cmd
set SILICONFLOW_API_KEY=sk-your-api-key-here
```

**永久设置：**
```cmd
setx SILICONFLOW_API_KEY "sk-your-api-key-here"
```

#### Linux/Mac

**临时设置：**
```bash
export SILICONFLOW_API_KEY="sk-your-api-key-here"
# 或
export OPENAI_API_KEY="sk-your-api-key-here"
```

**永久设置（添加到 ~/.bashrc 或 ~/.zshrc）：**
```bash
echo 'export SILICONFLOW_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ 验证配置是否成功

### 方法 1: 快速测试

```bash
python -c "import os; key = os.getenv('SILICONFLOW_API_KEY') or os.getenv('OPENAI_API_KEY'); print('✅ API Key 已设置' if key else '❌ API Key 未设置')"
```

### 方法 2: 测试 ETL Pipeline

```bash
python test_etl_pipeline.py
```

如果看到 "✅ 所有测试通过"，说明配置成功。

### 方法 3: 查看配置信息

```bash
python -c "from src.config import get_config; cfg = get_config(); print('API Key 已设置:', bool(cfg.api.api_key))"
```

---

## 🔍 项目如何读取 API Key

项目支持两种环境变量名（优先级从高到低）：

1. **`SILICONFLOW_API_KEY`** - 专用变量名
2. **`OPENAI_API_KEY`** - 兼容变量名

程序会按顺序检查这两个变量，找到第一个就使用。

### 读取位置

- **ETL Pipeline**: `src/etl_pipeline.py` - 使用 `get_api_key()` 函数
- **应用配置**: `src/config.py` - 使用 `python-dotenv` 加载 `.env` 文件

---

## 📝 .env 文件完整示例

完整的 `.env` 文件应该类似这样：

```env
# ============================================
# 无限流异世界恋爱 Visual Novel - 环境配置
# ============================================

# -------------------- API 配置 --------------------

# 方式 1: 使用专用变量名（推荐）
SILICONFLOW_API_KEY=sk-your-siliconflow-api-key-here

# 方式 2: 或使用兼容变量名（也可以）
# OPENAI_API_KEY=sk-your-siliconflow-api-key-here

# API 基础 URL（默认使用 SiliconFlow，一般不需要修改）
OPENAI_BASE_URL=https://api.siliconflow.cn/v1

# DeepSeek 对话模型（默认，一般不需要修改）
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3

# Flux 图像生成模型（默认，一般不需要修改）
FLUX_MODEL=black-forest-labs/FLUX.1-schnell

# API 请求超时时间（秒）
API_TIMEOUT=60

# API 请求最大重试次数
API_MAX_RETRIES=3

# -------------------- 其他配置（可选） --------------------

# 调试模式
DEBUG_MODE=false
```

---

## ⚠️ 注意事项

### 1. 安全提示

- ✅ **不要将 .env 文件提交到 Git**
- ✅ `.env` 文件已在 `.gitignore` 中
- ✅ 使用示例文件 `env.example` 作为模板
- ❌ 不要在代码中硬编码 API Key

### 2. 格式要求

- API Key 通常以 `sk-` 开头
- 不要包含引号（除非在系统环境变量中）
- 不要在等号前后有多余的空格

**正确格式：**
```env
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx
```

**错误格式：**
```env
SILICONFLOW_API_KEY = "sk-xxxxxxxxxxxxx"  # 有空格和引号
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxx  # 这行是对的，上面是错的
```

### 3. 重启要求

- 修改 `.env` 文件后，如果程序正在运行，需要重启
- 修改系统环境变量后，需要重启终端/IDE

### 4. API Key 格式

硅基流动的 API Key 格式通常是：
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

如果您的 Key 不是这个格式，请检查是否复制完整。

---

## 🐛 常见问题

### Q1: 提示 "请设置环境变量 SILICONFLOW_API_KEY"

**解决方法：**
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中的变量名是否正确
3. 确认 API Key 值已正确填写
4. 尝试使用 `SILICONFLOW_API_KEY` 而不是 `OPENAI_API_KEY`

### Q2: .env 文件不生效

**解决方法：**
1. 确认 `.env` 文件在项目根目录（与 `app.py` 同级）
2. 确认文件名为 `.env`（不是 `env.txt` 或 `.env.txt`）
3. 重启 Python 程序或 IDE
4. 检查文件编码为 UTF-8

### Q3: 如何确认 API Key 是否正确？

**测试方法：**
```python
from openai import AsyncOpenAI
import os

api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.siliconflow.cn/v1"
)

# 测试调用
import asyncio
async def test():
    response = await client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": "你好"}],
        max_tokens=10
    )
    print("✅ API Key 有效:", response.choices[0].message.content)

asyncio.run(test())
```

### Q4: 如何获取硅基流动 API Key？

1. 访问：https://cloud.siliconflow.cn
2. 注册/登录账户
3. 进入控制台
4. 找到「API 密钥」或「API Keys」页面
5. 创建新密钥或查看已有密钥
6. 复制密钥（通常只显示一次，请妥善保存）

---

## 📚 相关文档

- **项目配置说明**: `src/config.py`
- **ETL Pipeline 配置**: `src/etl_pipeline.py`
- **快速开始指南**: `快速开始.md`

---

## ✅ 配置检查清单

在运行 ETL Pipeline 或应用之前，请确认：

- [ ] 已获取硅基流动 API Key
- [ ] 已创建或编辑 `.env` 文件
- [ ] API Key 已正确填入 `.env` 文件
- [ ] 变量名使用 `SILICONFLOW_API_KEY` 或 `OPENAI_API_KEY`
- [ ] API Key 格式正确（通常以 `sk-` 开头）
- [ ] 已运行测试验证配置成功
- [ ] `.env` 文件未被提交到 Git（已在 .gitignore 中）

---

**配置完成后，您就可以运行 ETL Pipeline 或启动应用了！** 🚀



