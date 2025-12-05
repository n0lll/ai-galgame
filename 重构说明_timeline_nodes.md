# 📝 Timeline Nodes 重构说明

## ✅ 重构完成

已成功将 `WorldLore.timeline_nodes` 从简单的字符串列表重构为结构化的 `EventNode` 对象列表。

---

## 🎯 重构内容

### 1. 新增 `EventNode` 类

在 `WorldLore` 类之前添加了新的 Pydantic 模型：

```python
class EventNode(BaseModel):
    timestamp: str           # 灵活的时间表示
    summary: str             # 事件主要描述
    consequence: Optional[str]  # 因果影响（可选）
    involved_factions: List[str]  # 涉及的势力列表
    tags: List[str]          # 事件分类标签
```

**字段说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `timestamp` | `str` | ✅ | 灵活的时间表示（如 "Year 1024", "Spring Era 5"） |
| `summary` | `str` | ✅ | 事件的主要描述 |
| `consequence` | `Optional[str]` | ❌ | 该事件导致的因果影响（对 Logic Engine 至关重要） |
| `involved_factions` | `List[str]` | ❌ | 涉及的势力名称列表（引用 `WorldLore.factions`） |
| `tags` | `List[str]` | ❌ | 事件分类标签（如 ["War", "Magic", "Politics"]） |

---

### 2. 更新 `WorldLore.timeline_nodes`

**类型变更：**
```python
# 重构前
timeline_nodes: List[str]

# 重构后
timeline_nodes: List[EventNode]
```

**优势：**
- ✅ 结构化数据，便于逻辑推理
- ✅ 支持因果关系追踪
- ✅ 支持按标签和势力过滤
- ✅ 更丰富的元数据支持

---

### 3. 严格保留的字段

✅ **`villian_type`** (WorldLore) - 完全保留，未修改  
✅ **`possible_ending`** (RomanceScript) - 完全保留，未修改

---

## 📊 使用示例

### 创建事件节点

```python
from src.models import EventNode, WorldLore

# 创建事件节点
event = EventNode(
    timestamp="Year 1024, Spring Semester",
    summary="新生入学典礼：主角正式进入魔法学院",
    consequence="主角被分配到火焰院，开始接触学院的核心课程",
    involved_factions=["光明议会"],
    tags=["School", "Important", "Turning Point"]
)

# 创建 WorldLore
world_lore = WorldLore(
    timeline_nodes=[event],
    factions={"光明议会": "学院管理机构"},
    villian_type="黑暗势力..."  # 保留字段
)
```

### 访问和过滤

```python
# 访问第一个事件
first_event = world_lore.timeline_nodes[0]
print(f"时间: {first_event.timestamp}")
print(f"摘要: {first_event.summary}")
print(f"影响: {first_event.consequence}")

# 按标签过滤
important_events = [
    e for e in world_lore.timeline_nodes 
    if "Important" in e.tags
]

# 按势力过滤
faction_events = [
    e for e in world_lore.timeline_nodes
    if "光明议会" in e.involved_factions
]

# 查找有因果关系的事件
causal_events = [
    e for e in world_lore.timeline_nodes
    if e.consequence is not None
]
```

---

## 🔄 迁移指南

### 旧代码（字符串列表）

```python
world_lore = WorldLore(
    timeline_nodes=[
        "春季开学：新生入学典礼",
        "第一次实战课：展现天赋",
        "秋季祭典：与女主相识"
    ]
)
```

### 新代码（EventNode 列表）

```python
world_lore = WorldLore(
    timeline_nodes=[
        EventNode(
            timestamp="Year 1024, Spring",
            summary="春季开学：新生入学典礼",
            consequence="主角开始学院生活",
            involved_factions=["光明议会"],
            tags=["School", "Important"]
        ),
        EventNode(
            timestamp="Year 1024, Mid-Spring",
            summary="第一次实战课：展现天赋",
            consequence="引起教师注意",
            involved_factions=[],
            tags=["Magic"]
        ),
        EventNode(
            timestamp="Year 1024, Autumn",
            summary="秋季祭典：与女主相识",
            consequence="建立初始联系",
            involved_factions=[],
            tags=["Romance"]
        )
    ]
)
```

---

## ✅ 测试验证

运行测试脚本验证重构：

```bash
python test_timeline_refactor.py
```

**测试结果：**
- ✅ EventNode 类正确定义
- ✅ WorldLore.timeline_nodes 类型为 List[EventNode]
- ✅ villian_type 字段保留
- ✅ possible_ending 字段保留
- ✅ 序列化/反序列化正常
- ✅ 字段访问正常

---

## 🎯 Logic Engine 使用建议

### 1. 因果关系追踪

```python
def find_causal_chain(events: List[EventNode], target_summary: str):
    """查找导致某个事件的所有原因"""
    causal_chain = []
    for event in events:
        if target_summary in (event.consequence or ""):
            causal_chain.append(event)
            # 递归查找原因的原因
            causal_chain.extend(find_causal_chain(events, event.summary))
    return causal_chain
```

### 2. 按时间排序

```python
# Logic Engine 可以按 timestamp 排序事件
sorted_events = sorted(
    world_lore.timeline_nodes,
    key=lambda e: e.timestamp
)
```

### 3. 筛选相关事件

```python
def get_relevant_events(
    world_lore: WorldLore,
    current_tags: List[str],
    current_factions: List[str]
):
    """根据当前上下文筛选相关事件"""
    relevant = []
    for event in world_lore.timeline_nodes:
        # 检查标签匹配
        if any(tag in event.tags for tag in current_tags):
            relevant.append(event)
        # 检查势力匹配
        elif any(faction in event.involved_factions 
                 for faction in current_factions):
            relevant.append(event)
    return relevant
```

---

## 📝 注意事项

1. **向后兼容性**
   - 旧代码使用字符串列表将无法直接工作
   - 需要将现有数据迁移为 EventNode 格式

2. **consequence 字段**
   - 虽然可选，但强烈建议为关键转折点事件填写
   - 这将大大提高 Logic Engine 的推理能力

3. **involved_factions**
   - 必须引用 `WorldLore.factions` 中已定义的势力名称
   - 空列表表示事件不涉及特定势力

4. **tags 建议**
   - 使用一致的标签命名（如 "School", "Magic", "Romance"）
   - 每个事件包含 2-5 个标签
   - 可以创建标签分类文档供参考

---

## 🎉 重构优势总结

| 方面 | 重构前 | 重构后 |
|------|--------|--------|
| **数据结构** | 简单字符串 | 结构化对象 |
| **因果关系** | 无法追踪 | 支持因果关系 |
| **过滤查询** | 文本匹配 | 结构化查询 |
| **时间管理** | 不明确 | 明确的 timestamp |
| **势力关联** | 无 | 明确的 faction 关联 |
| **分类检索** | 困难 | 标签系统支持 |
| **Logic Engine** | 文本解析 | 直接访问结构化数据 |

---

**重构完成！** 🎉

现在 `timeline_nodes` 提供了更强大的数据结构，支持更复杂的逻辑推理和事件管理。



