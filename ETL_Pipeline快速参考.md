# ⚡ ETL Pipeline 快速参考

## 🚀 快速开始

### 1. 准备文件

```bash
# 确保有输入文件
data/
  ├── world_novel_cleaned.txt      # 世界观小说
  └── romance_novel_cleaned.txt    # 恋爱小说
```

### 2. 设置 API Key

```bash
# .env 文件
SILICONFLOW_API_KEY=your_key_here
```

### 3. 运行 Pipeline

```bash
python src/etl_pipeline.py
```

### 4. 查看输出

```bash
output/
  ├── world_lore.json          # 世界观数据
  ├── romance_script.json      # 恋爱数据
  └── heroine_profile.json     # 女主设定（可选）
```

---

## 📋 核心类速查

| 类 | 功能 | 输出 |
|----|------|------|
| `NovelLoader` | 文本切片 | `List[str]` |
| `DeepSeekExtractor` | Map 提取 | `PartialWorldLore` / `PartialRomanceData` |
| `HeroineSynthesizer` | Reduce 合成 | `(psychological_profile, speech_pattern)` |
| `DataAggregator` | Reduce 聚合 | `WorldLore` / `RomanceScript` |

---

## 🎯 关键字段保护

✅ **严格保留的字段**：
- `WorldLore.villian_type` - 反派类型
- `RomanceScript.possible_ending` - 可能结局

---

## ⚙️ 配置参数

```python
# src/etl_pipeline.py

MAX_CONCURRENT_REQUESTS = 8    # 并发数（5-10）
CHUNK_SIZE_TOKENS = 3000       # 块大小
OVERLAP_TOKENS = 500          # 重叠大小
MODEL_NAME = "deepseek-ai/DeepSeek-V3"
```

---

## 📊 数据流程

```
TXT 文件
  ↓
NovelLoader (切片)
  ↓
文本块 [Chunk1, Chunk2, ...]
  ↓
DeepSeekExtractor (并行提取 - Map)
  ↓
碎片数据 [Partial1, Partial2, ...]
  ↓
DataAggregator (聚合 - Reduce)
  ↓
结构化数据 (JSON)
```

---

## 🔧 故障排除

| 问题 | 解决方法 |
|------|----------|
| API Key 错误 | 检查 `.env` 文件 |
| 文件不存在 | 准备输入文件或 Pipeline 会跳过 |
| API 限流 | 降低 `MAX_CONCURRENT_REQUESTS` |
| JSON 解析错误 | 自动处理，失败的块返回空对象 |

---

## 📝 验证输出

```python
from src.models import WorldLore, RomanceScript
import json

# 验证世界观
with open("output/world_lore.json") as f:
    world_lore = WorldLore.model_validate_json(f.read())

# 验证恋爱数据
with open("output/romance_script.json") as f:
    romance_script = RomanceScript.model_validate_json(f.read())
```

---

## 🎯 测试

```bash
# 运行组件测试
python test_etl_pipeline.py

# 运行完整 Pipeline
python src/etl_pipeline.py
```

---

**详细信息请查看 `ETL_Pipeline使用说明.md`**



