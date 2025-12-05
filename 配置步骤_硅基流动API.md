# 🔑 配置硅基流动 API Key - 详细步骤

## ✅ 当前状态

检查结果显示：您的 `.env` 文件中 API Key 还是默认值 `your_api_key_here`，需要替换为真实的 API Key。

---

## 🚀 配置步骤（3 步完成）

### 步骤 1: 获取硅基流动 API Key

1. **访问硅基流动控制台**
   - 网址：https://cloud.siliconflow.cn
   - 使用浏览器打开

2. **登录/注册账户**
   - 如果没有账户，先注册
   - 如果已有账户，直接登录

3. **找到 API 密钥页面**
   - 登录后，进入控制台
   - 找到「API 密钥」或「API Keys」菜单
   - 或直接访问：https://cloud.siliconflow.cn/settings/api-keys

4. **创建或查看 API Key**
   - 如果已有 API Key，直接复制
   - 如果没有，点击「创建新密钥」或「Create API Key」
   - **重要**：API Key 通常只显示一次，请妥善保存

5. **复制 API Key**
   - API Key 格式通常类似：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - 完整复制整个 Key（不要遗漏）

---

### 步骤 2: 编辑 .env 文件

#### 方法 A: 使用文本编辑器（推荐）

1. **找到 .env 文件**
   - 位置：项目根目录（与 `app.py` 同级）
   - 文件名：`.env`

2. **用文本编辑器打开**
   - Windows：可以用记事本、VS Code、Notepad++ 等
   - 右键点击 `.env` 文件 → 选择「打开方式」→ 选择文本编辑器

3. **找到并修改这一行**
   
   找到：
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```
   
   替换为（将 `sk-您的真实API密钥` 替换为您刚才复制的 Key）：
   ```env
   OPENAI_API_KEY=sk-您的真实API密钥
   ```
   
   **示例**（假设您的 Key 是 `sk-abc123def456...`）：
   ```env
   OPENAI_API_KEY=sk-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
   ```

4. **保存文件**
   - 按 `Ctrl + S` 保存
   - 确保文件编码是 UTF-8

#### 方法 B: 使用命令行（Windows PowerShell）

```powershell
# 1. 获取您的 API Key（手动输入或从剪贴板）
$apiKey = Read-Host "请输入您的硅基流动 API Key"

# 2. 更新 .env 文件
(Get-Content .env) -replace 'OPENAI_API_KEY=your_api_key_here', "OPENAI_API_KEY=$apiKey" | Set-Content .env

Write-Host "✅ API Key 已更新"
```

#### 方法 C: 使用命令行（Linux/Mac）

```bash
# 编辑 .env 文件
nano .env
# 或
vim .env

# 找到 OPENAI_API_KEY=your_api_key_here
# 替换为您的真实 Key
# 保存退出
```

---

### 步骤 3: 验证配置

运行检查脚本验证配置是否成功：

```bash
python check_api_key.py
```

如果看到以下输出，说明配置成功：

```
✅ API Key 配置正确！
🎉 所有检查通过！
```

---

## 📝 完整 .env 文件示例

配置完成后的 `.env` 文件应该类似这样：

```env
# ============================================
# 无限流异世界恋爱 Visual Novel - 环境配置
# ============================================

# -------------------- API 配置 --------------------

# 硅基流动 API 密钥（必填）
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 或者使用专用变量名（两种方式都可以）：
# SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

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

# ... 其他配置 ...
```

---

## ⚠️ 重要注意事项

### 1. 安全提示

- ✅ **.env 文件已在 .gitignore 中**，不会被提交到 Git
- ✅ **不要在任何公开场合分享您的 API Key**
- ✅ **不要在代码中硬编码 API Key**

### 2. 格式要求

- API Key 不要包含引号
- 不要在等号前后有空格
- 确保 Key 完整（没有遗漏）

**正确：**
```env
OPENAI_API_KEY=sk-abc123def456...
```

**错误：**
```env
OPENAI_API_KEY = "sk-abc123def456..."  # 有空格和引号
OPENAI_API_KEY=sk-abc123def45         # Key 不完整
```

### 3. 两种变量名都可以

项目支持两种环境变量名：

1. `SILICONFLOW_API_KEY` - 专用名称（推荐）
2. `OPENAI_API_KEY` - 兼容名称（也可以）

**您可以选择其中一种设置，或者两种都设置（会优先使用 `SILICONFLOW_API_KEY`）**

---

## 🔍 验证配置

### 方法 1: 使用检查脚本（推荐）

```bash
python check_api_key.py
```

### 方法 2: 快速测试

```bash
python -c "from src.etl_pipeline import get_api_key; key = get_api_key(); print('✅ 配置成功:', key[:10] + '...')"
```

### 方法 3: 运行 ETL Pipeline 测试

```bash
python test_etl_pipeline.py
```

如果所有测试通过，说明配置正确。

---

## 🐛 常见问题

### Q1: 找不到 API Key 在哪里获取？

**答案**：
1. 访问：https://cloud.siliconflow.cn
2. 登录后，点击右上角头像或进入「设置」
3. 找到「API 密钥」或「API Keys」选项
4. 如果找不到，可以直接访问：https://cloud.siliconflow.cn/settings/api-keys

### Q2: API Key 格式是什么？

**答案**：硅基流动的 API Key 通常：
- 以 `sk-` 开头
- 长度约 40-60 个字符
- 格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Q3: 配置后还是提示未设置？

**解决方法**：
1. 确认 `.env` 文件在项目根目录（与 `app.py` 同级）
2. 确认文件名是 `.env`（不是 `.env.txt` 或其他）
3. 确认变量名正确（`OPENAI_API_KEY` 或 `SILICONFLOW_API_KEY`）
4. 重启终端或 IDE
5. 检查 API Key 值是否正确（没有多余空格）

### Q4: 可以同时设置两个变量吗？

**答案**：可以，但程序会优先使用 `SILICONFLOW_API_KEY`。建议只设置一个。

### Q5: 修改 .env 后需要重启吗？

**答案**：
- 如果 Python 程序正在运行，需要重启
- 如果只是修改文件，新启动的程序会自动加载

---

## 🎯 配置完成后的下一步

配置完成后，您可以：

1. **运行 ETL Pipeline**：
   ```bash
   python src/etl_pipeline.py
   ```

2. **运行 Streamlit 应用**：
   ```bash
   streamlit run app.py
   ```

3. **测试组件**：
   ```bash
   python test_etl_pipeline.py
   ```

---

## 📚 相关文档

- **快速配置指南**: `配置API_Key_快速指南.md`
- **详细配置说明**: `配置API_Key指南.md`
- **检查脚本**: `check_api_key.py`

---

## ✅ 配置检查清单

配置完成后，请确认：

- [ ] 已从硅基流动控制台获取 API Key
- [ ] 已编辑 `.env` 文件
- [ ] API Key 已正确填入（不是 `your_api_key_here`）
- [ ] API Key 格式正确（以 `sk-` 开头）
- [ ] 已运行 `python check_api_key.py` 验证
- [ ] 验证结果显示 "✅ 配置正确"

---

**完成配置后，就可以开始使用 ETL Pipeline 提取数据了！** 🚀



