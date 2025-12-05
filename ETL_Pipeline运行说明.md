# ETL Pipeline 运行说明

## 🚀 运行方式

### 方式 1: 直接运行脚本（推荐）

从项目根目录运行：

```powershell
# Windows PowerShell
python .\src\etl_pipeline.py

# 或者使用完整路径
python src/etl_pipeline.py
```

**注意**：脚本已经自动处理路径问题，可以直接运行。

### 方式 2: 作为模块运行

从项目根目录运行：

```powershell
# Windows PowerShell
python -m src.etl_pipeline
```

## ⚠️ 常见错误及解决方案

### 错误 1: `ModuleNotFoundError: No module named 'src'`

**原因**：Python 无法找到 `src` 模块。

**解决方案**：
1. 确保在**项目根目录**运行命令
2. 如果问题仍然存在，使用方式 2（作为模块运行）

### 错误 2: `ValueError: 请设置环境变量 SILICONFLOW_API_KEY 或 OPENAI_API_KEY`

**原因**：未设置 API Key。

**解决方案**：
1. 在 `.env` 文件中设置 `SILICONFLOW_API_KEY` 或 `OPENAI_API_KEY`
2. 或者设置环境变量：
   ```powershell
   $env:SILICONFLOW_API_KEY="your_api_key_here"
   python .\src\etl_pipeline.py
   ```

### 错误 3: 文件不存在

**原因**：缺少输入文件。

**解决方案**：
1. 确保 `data/world_novel_cleaned.txt` 存在
2. 确保 `data/romance_novel_cleaned.txt` 存在
3. 或者修改脚本中的文件路径

## 📋 运行前检查清单

- [ ] 已安装所有依赖：`pip install -r requirements.txt`
- [ ] 已设置 API Key（在 `.env` 文件或环境变量中）
- [ ] 输入文件已准备（`data/world_novel_cleaned.txt` 和 `data/romance_novel_cleaned.txt`）
- [ ] 在项目根目录运行命令

## 🔧 运行示例

```powershell
# 1. 进入项目根目录
cd D:\cursor-project\ai-galgame

# 2. 检查 API Key 是否设置（可选）
python check_api_key.py

# 3. 运行 ETL Pipeline
python .\src\etl_pipeline.py
```

## 📝 输出说明

运行成功后，会在 `output/` 目录生成以下文件：

- `world_lore.json` - 世界观数据
- `romance_script.json` - 恋爱脚本数据
- `heroine_profile.json` - 女主角设定数据

## 💡 提示

- 如果遇到导入错误，尝试使用 `python -m src.etl_pipeline` 运行
- 查看控制台输出了解处理进度
- 大文件处理可能需要较长时间，请耐心等待

