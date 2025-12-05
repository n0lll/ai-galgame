# 📚 ETL Pipeline 使用说明

## 🎯 功能概述

ETL Pipeline 是一个数据提取管道，用于从清洗后的 TXT 小说文件中提取结构化数据，并转换为符合 `src/models.py` 定义的高密度结构化数据。

### 核心特性

- ✅ **Map-Reduce 架构**：高效处理长文本
- ✅ **并发处理**：使用异步 API 调用，支持并行提取
- ✅ **结构化输出**：严格符合 Pydantic 模型定义
- ✅ **深度分析**：支持女主心理侧写和说话风格合成
- ✅ **数据保护**：严格保留 `villian_type` 和 `possible_ending` 字段

---

## 📦 架构组件

### 1. NovelLoader（文本切片器）

**功能**：将长文本按 Token 窗口切分

- **块大小**：~3000 tokens（约 12000 字符）
- **重叠**：500 tokens（约 2000 字符）
- **用途**：确保上下文连贯性，避免在句子中间截断

### 2. DeepSeekExtractor（核心提取器 - Map Step）

**功能**：从文本块中提取结构化信息

**两个核心方法**：

1. `extract_world_chunk()` - 提取世界观数据
   - 提取规则、地点、时间线事件、势力
   - 提取反派类型特征
   - 输出 `PartialWorldLore`

2. `extract_romance_chunk()` - 提取恋爱数据
   - 提取互动事件
   - 收集女主台词原句（`dialogue_snippets`）
   - 收集心理描写片段（`psychology_clues`）
   - 预测可能结局
   - 输出 `PartialRomanceData`

### 3. HeroineSynthesizer（女主合成器 - Reduce Step）

**功能**：将收集的素材汇总，生成深度女主设定

- **输入**：所有对话片段、心理线索、互动事件
- **输出**：
  - `psychological_profile`：深度心理侧写
  - `speech_pattern`：说话风格描述（含 Few-Shot 示例）

### 4. DataAggregator（数据聚合器 - Reduce Step）

**功能**：合并所有 Chunk 的提取结果

**合并策略**：

- **时间线事件**：按 `timestamp` 排序并去重
- **反派类型**：统计频率，选择最连贯的描述
- **可能结局**：汇总去重
- **地点/势力**：字典合并，保留更详细的描述

---

## 🚀 使用方法

### 前置准备

1. **准备输入文件**：

   ```
   data/
     ├── world_novel_cleaned.txt      # 世界观小说（清洗后）
     └── romance_novel_cleaned.txt    # 恋爱小说（清洗后）
   ```

2. **设置环境变量**：

   ```bash
   # .env 文件或系统环境变量
   SILICONFLOW_API_KEY=your_api_key_here
   # 或
   OPENAI_API_KEY=your_api_key_here
   ```

3. **安装依赖**：

   ```bash
   pip install openai pydantic
   ```

### 运行 Pipeline

```bash
python src/etl_pipeline.py
```

### 输出结果

Pipeline 会在 `output/` 目录生成以下文件：

```
output/
  ├── world_lore.json          # 世界观知识库
  ├── romance_script.json      # 恋爱剧本知识库
  └── heroine_profile.json     # 女主设定（可选）
```

---

## 📋 配置参数

### 可调整的常量

在 `src/etl_pipeline.py` 文件顶部：

```python
# 并发控制
MAX_CONCURRENT_REQUESTS = 8  # 并发请求数（建议 5-10）

# Token 窗口
CHUNK_SIZE_TOKENS = 3000     # 每块大小（tokens）
OVERLAP_TOKENS = 500         # 重叠大小（tokens）

# API 配置
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"
```

### 调整建议

- **并发数**：根据 API 限制调整，建议 5-10
- **块大小**：较大的块能保留更多上下文，但会增加处理时间
- **重叠**：较大的重叠能减少信息丢失，但会增加重复提取

---

## 📊 数据流程

```
输入文件 (TXT)
    ↓
NovelLoader（切片）
    ↓
文本块列表 [Chunk1, Chunk2, ...]
    ↓
DeepSeekExtractor（并行提取 - Map）
    ↓
碎片数据列表 [Partial1, Partial2, ...]
    ↓
DataAggregator（聚合 - Reduce）
    ↓
结构化数据 (WorldLore / RomanceScript)
    ↓
输出文件 (JSON)
```

### 恋爱数据特殊流程

```
PartialRomanceData 列表
    ↓
收集所有 dialogue_snippets 和 psychology_clues
    ↓
HeroineSynthesizer（合成女主设定 - Reduce）
    ↓
psychological_profile + speech_pattern
    ↓
与聚合后的 RomanceScript 合并
    ↓
最终输出
```

---

## ⚠️ 注意事项

### 1. API 限制

- SiliconFlow API 有速率限制
- 使用 `asyncio.Semaphore` 控制并发数
- 如果遇到限流，自动重试（最多 3 次）

### 2. Token 估算

当前使用简单的字符数估算（1 token ≈ 4 字符）

- 这是保守估计，实际可能更少
- 如果文本包含大量标点、数字，可能需要调整

### 3. 数据完整性

- **关键字段保护**：`villian_type` 和 `possible_ending` 严格保留
- **去重机制**：自动去除重复的事件、对话、结局
- **数据验证**：使用 Pydantic 确保数据结构正确

### 4. 错误处理

- 单个 Chunk 提取失败不会中断整个流程
- 失败的 Chunk 会返回空对象
- 最终聚合时会自动处理缺失数据

---

## 🔧 故障排除

### 问题 1: API Key 错误

**错误信息**：
```
ValueError: 请设置环境变量 SILICONFLOW_API_KEY 或 OPENAI_API_KEY
```

**解决方法**：
1. 检查 `.env` 文件是否存在
2. 确认环境变量名称正确
3. 重启终端/IDE 使环境变量生效

### 问题 2: 文件不存在

**错误信息**：
```
FileNotFoundError: 文件不存在: data/world_novel_cleaned.txt
```

**解决方法**：
1. 检查文件路径是否正确
2. 确认文件已准备好
3. 如果没有文件，Pipeline 会跳过并显示警告

### 问题 3: API 调用失败

**错误信息**：
```
[警告] API 调用失败（已重试 3 次）: ...
```

**解决方法**：
1. 检查网络连接
2. 确认 API Key 有效
3. 检查 API 余额
4. 降低并发数（`MAX_CONCURRENT_REQUESTS`）

### 问题 4: JSON 解析错误

**错误信息**：
```
json.JSONDecodeError: ...
```

**解决方法**：
1. 这通常是 AI 返回格式不正确
2. Pipeline 会尝试提取 JSON 代码块
3. 如果仍然失败，该 Chunk 会返回空对象

---

## 📈 性能优化建议

### 1. 并发数调整

```python
# 如果 API 限制较宽松
MAX_CONCURRENT_REQUESTS = 10

# 如果经常遇到限流
MAX_CONCURRENT_REQUESTS = 5
```

### 2. 块大小优化

```python
# 对于细节丰富的小说
CHUNK_SIZE_TOKENS = 4000  # 更大的块

# 对于简单的小说
CHUNK_SIZE_TOKENS = 2000  # 更小的块，更快处理
```

### 3. 分批处理

对于超长小说，可以：
1. 手动分割文件
2. 分别处理
3. 手动合并结果

---

## 🔍 输出数据验证

### 验证 WorldLore

```python
from src.models import WorldLore
import json

with open("output/world_lore.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 使用 Pydantic 验证
world_lore = WorldLore.model_validate(data)

# 检查关键字段
print(f"规则数量: {len(world_lore.rules)}")
print(f"事件数量: {len(world_lore.timeline_nodes)}")
print(f"反派类型: {world_lore.villian_type or '未提取'}")
```

### 验证 RomanceScript

```python
from src.models import RomanceScript
import json

with open("output/romance_script.json", "r", encoding="utf-8") as f:
    data = json.load(f)

romance_script = RomanceScript.model_validate(data)

print(f"互动事件: {len(romance_script.interaction_events)}")
print(f"对话范例: {len(romance_script.dialogue_examples)}")
print(f"可能结局: {len(romance_script.possible_ending)}")
```

---

## 📝 示例输出

### world_lore.json 结构

```json
{
  "rules": [
    "魔法需要通过咒语和手势施展",
    "不同种族拥有不同的魔法亲和力"
  ],
  "locations": {
    "星辰魔法学院": "建立于500年前的顶尖魔法学府..."
  },
  "timeline_nodes": [
    {
      "timestamp": "Year 1024, Spring",
      "summary": "春季开学：新生入学典礼",
      "consequence": "主角开始学院生活",
      "involved_factions": ["光明议会"],
      "tags": ["School", "Important"]
    }
  ],
  "factions": {
    "光明议会": "学院的管理机构..."
  },
  "lore_summary": "...",
  "villian_type": "黑暗势力：追求权力和控制..."
}
```

### romance_script.json 结构

```json
{
  "interaction_events": [
    {
      "event_name": "图书馆初遇",
      "description": "...",
      "emotional_shift": "从陌生到好奇",
      "affection_change": 5,
      "key_dialogue": "..."
    }
  ],
  "dialogue_examples": [
    "你这个笨蛋...",
    "如果是你的话..."
  ],
  "relationship_stages": [
    "初识：图书馆偶遇",
    "好感：开始期待再次相遇"
  ],
  "emotional_triggers": {
    "送礼物": "惊喜并感动..."
  },
  "possible_ending": [
    "圆满结局：两人最终走到一起",
    "悲剧结局：因误会分离"
  ],
  "romance_summary": "..."
}
```

---

## 🎯 下一步

提取完成后，您可以：

1. **验证数据质量**：检查提取的字段是否完整
2. **手动调整**：根据需要编辑 JSON 文件
3. **集成到游戏**：使用提取的数据初始化 `GameState`
4. **创建女主**：使用 `heroine_profile.json` 创建 `Heroine` 对象

---

## 📚 相关文档

- `架构升级说明_双小说驱动.md` - 数据结构说明
- `src/models.py` - 数据模型定义
- `example_dual_novel.py` - 使用示例

---

**祝提取顺利！** 🚀



