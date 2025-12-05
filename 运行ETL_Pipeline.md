# 运行 ETL Pipeline - 快速指南

## ✅ 问题已修复

`ModuleNotFoundError: No module named 'src'` 问题已经修复。现在可以直接运行脚本了。

## 🚀 运行方式

### 从项目根目录运行（推荐）

```powershell
python .\src\etl_pipeline.py
```

或者：

```powershell
python src/etl_pipeline.py
```

### 作为模块运行（备选）

```powershell
python -m src.etl_pipeline
```

## ⚠️ 运行前检查

1. **确保在项目根目录**：`D:\cursor-project\ai-galgame`
2. **确保 API Key 已设置**：
   - 在 `.env` 文件中设置 `SILICONFLOW_API_KEY` 或 `OPENAI_API_KEY`
   - 或设置环境变量
3. **确保输入文件存在**：
   - `data/world_novel_cleaned.txt`
   - `data/romance_novel_cleaned.txt`

## 🔧 修复说明

已在 `src/etl_pipeline.py` 文件开头添加了路径处理代码：

```python
# 添加项目根目录到 Python 路径（支持直接运行脚本）
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
```

这样可以直接运行脚本，无需修改 Python 路径或使用模块方式运行。

## 📝 示例运行

```powershell
# 1. 进入项目根目录
cd D:\cursor-project\ai-galgame

# 2. 运行 ETL Pipeline
python .\src\etl_pipeline.py
```

## ❓ 如果还有问题

1. 确认当前目录：运行 `pwd` 或 `Get-Location`
2. 检查 Python 版本：运行 `python --version`（需要 Python 3.10+）
3. 检查依赖：运行 `pip install -r requirements.txt`

