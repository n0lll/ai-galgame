# 🔑 硅基流动 API Key 快速配置指南

## ⚡ 最简单的方法（3 步完成）

### 步骤 1: 获取 API Key

1. 打开浏览器，访问：**https://cloud.siliconflow.cn**
2. 登录您的账户
3. 在控制台中找到「API 密钥」或「API Keys」页面
4. 复制您的 API Key（格式类似：`sk-xxxxxxxxxxxxx`）

### 步骤 2: 编辑 .env 文件

在项目根目录找到 `.env` 文件（与 `app.py` 同级），用文本编辑器打开。

找到这一行：
```env
OPENAI_API_KEY=your_api_key_here
```

替换为您的真实 API Key：
```env
OPENAI_API_KEY=sk-您的真实API密钥
```

**或者**，您也可以使用专用变量名（两种方式都可以）：
```env
SILICONFLOW_API_KEY=sk-您的真实API密钥
```

### 步骤 3: 保存文件

保存 `.env` 文件，完成！

---

## ✅ 验证配置

运行这个命令验证：

```bash
python -c "from src.etl_pipeline import get_api_key; key = get_api_key(); print('✅ API Key 配置成功！'); print('   前10个字符:', key[:10] + '...')"
```

如果显示 "✅ API Key 配置成功！"，说明配置正确。

---

## 📝 完整示例

您的 `.env` 文件应该类似这样：

```env
# API 配置
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 或使用
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 其他配置（默认值，一般不需要修改）
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3
```

---

## 🎯 重要提示

1. **不要提交 .env 文件到 Git** - 它已经在 `.gitignore` 中了
2. **API Key 以 `sk-` 开头** - 如果您的 Key 不是这个格式，请检查
3. **保存后需要重启程序** - 如果 Python 程序正在运行，需要重启

---

## 🐛 遇到问题？

### 问题：找不到 .env 文件

**解决**：从 `env.example` 复制一个
```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

### 问题：配置后还是提示未设置

**解决**：
1. 确认文件名是 `.env`（不是 `.env.txt`）
2. 确认文件在项目根目录
3. 重启终端或 IDE
4. 检查 API Key 格式是否正确

### 问题：如何获取 API Key？

**步骤**：
1. 访问：https://cloud.siliconflow.cn
2. 登录账户
3. 进入控制台 → API 密钥页面
4. 创建新密钥或查看已有密钥
5. 复制密钥（请妥善保存）

---

## 📚 详细说明

查看 `配置API_Key指南.md` 获取更详细的配置说明和故障排除方法。

---

**配置完成后，就可以运行 `python src/etl_pipeline.py` 了！** 🚀



