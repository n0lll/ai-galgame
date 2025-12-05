# 📝 models.py 重构说明 - 纯剧情向 Visual Novel

## 🎯 重构目标

将项目从 RPG 风格调整为**纯剧情向 Visual Novel**，移除所有战斗和消耗品系统，专注于角色关系、情感发展和剧情叙事。

---

## ✨ 主要修改内容

### 1. Character 类 - 角色数据模型

#### 🔄 修改的字段

**`stats` 字段 - 关系型数值（重要修改）**
```python
stats: Dict[str, Any] = Field(
    default_factory=dict,
    description="""
    关系型数值字典 - 仅用于存储影响剧情走向的情感/心理数值。
    推荐字段：
      - affection (好感度): 0-100
      - trust (信任度): 0-100
      - dominance (支配度): -100 到 100
      - stress (压力值): 0-100
      - intimacy (亲密度): 0-100
    
    ⚠️ 严禁包含战斗数值（如 HP、MP、攻击力、防御力等）
    """
)
```

**关键点：**
- ✅ 明确标注此字段**仅用于关系型数值**
- ✅ 提供了推荐的情感/心理数值字段
- ⚠️ **严禁**包含任何战斗相关数值

#### ➕ 新增的字段

**`memory_buffer` - 角色记忆缓冲区（核心新增）**
```python
memory_buffer: List[str] = Field(
    default_factory=list,
    description="""
    角色记忆缓冲区 - 存储该角色经历过的关键事件摘要。
    用途：保持剧情连贯性，让 AI 记住角色的重要经历。
    示例：["记得玩家在雨中送过伞", "曾在咖啡厅与玩家约会", "知道玩家的秘密"]
    建议：每个摘要不超过 50 字，保留最近 20-30 条重要记忆
    """
)
```

**用途：**
- 🧠 让角色"记住"与玩家的重要互动
- 📖 保持剧情连贯性，防止 AI 遗忘前期设定
- 💡 为后续对话生成提供上下文

#### 🔧 优化的字段

**`weight` - 添加了数值范围验证**
```python
weight: int = Field(
    default=0,
    ge=0,  # 最小值 0
    le=100,  # 最大值 100
    description="角色权重 (0-100)，影响该角色对剧情的影响程度"
)
```

**`related_characters` - 优化了格式说明**
```python
related_characters: List[Dict[str, str]] = Field(
    default_factory=list,
    description="""
    与该角色相关联的角色关系列表。
    格式：[{"character_id": "char_002", "relationship": "青梅竹马"}, ...]
    关系类型示例：朋友、恋人、竞争对手、家人、师徒等
    """
)
```

---

### 2. GameState 类 - 游戏状态模型

#### 🔄 重命名的字段

**`inventory` → `key_items`（重要改名）**
```python
# 旧名称
inventory: List[str]  # 玩家背包物品列表

# 新名称
key_items: List[str] = Field(
    default_factory=list,
    description="""
    关键道具列表 - 仅存储影响剧情分支的重要物品。
    示例：["定情信物", "未寄出的信", "神秘钥匙", "旧照片"]
    
    ⚠️ 不存储消耗品（如药水、食物等），这是纯剧情向 VN，非 RPG
    """
)
```

**改名原因：**
- 📦 `inventory` 暗示 RPG 风格的背包系统
- 🔑 `key_items` 更符合 VN 的关键道具概念

#### 🔄 优化的字段

**`turn_count` - 重新定义为剧情节奏计数器**
```python
turn_count: int = Field(
    default=0,
    ge=0,  # 添加了非负验证
    description="剧情节奏计数器 - 记录当前是第几个回合/场景，用于控制剧情推进速度"
)
```

#### ➕ 新增的字段

**`current_phase` - 剧情阶段标记（核心新增）**
```python
current_phase: str = Field(
    default="intro",
    description="""
    当前剧情阶段标记，用于控制叙事节奏和 AI 生成内容的风格。
    可选值：
      - intro: 序章/开场，介绍世界观和角色
      - rising_action: 发展阶段，矛盾逐渐显现
      - climax: 高潮阶段，冲突达到顶峰
      - resolution: 结局/收尾，故事走向终点
    """
)
```

**用途：**
- 🎬 控制叙事节奏（三幕剧结构）
- 🎨 影响 AI 生成内容的风格和强度
- 📊 帮助跟踪剧情进度

**`narrative_summary` - 全局剧情摘要（核心新增）**
```python
narrative_summary: str = Field(
    default="",
    description="""
    全局剧情摘要 - 用于解决长篇剧情的上下文窗口限制。
    记录整体故事的关键发展、重要选择和结果，防止 AI 在 50 回合后忘记前期设定。
    建议：每 10-20 回合更新一次，保持在 500-1000 字以内。
    """
)
```

**用途：**
- 🔄 解决上下文窗口限制问题
- 📝 防止长篇剧情中 AI 遗忘前期设定
- 💾 压缩存储长期剧情信息

---

### 3. GameConfig 类 - 游戏配置

#### ➕ 新增的字段

**`narrative_style` - 叙事风格偏好**
```python
narrative_style: str = Field(
    default="romantic",
    description="""
    叙事风格偏好，影响 AI 生成内容的基调。
    可选：romantic (浪漫), dramatic (戏剧性), slice_of_life (日常), mystery (悬疑)
    """
)
```

#### 🔧 优化的字段

**`difficulty` - 重新定义为选项复杂度**
```python
difficulty: str = Field(
    default="normal",
    description="""
    游戏难度 - 在 VN 中影响选项的复杂度和结局达成难度。
    可选值：easy (明确提示), normal (适度提示), hard (无提示)
    """
)
```

**`text_speed` - 添加了数值范围验证**
```python
text_speed: float = Field(
    default=1.0,
    ge=0.5,  # 最小 0.5x
    le=3.0,  # 最大 3.0x
    description="文本显示速度倍率（0.5 = 慢速, 1.0 = 正常, 2.0 = 快速）"
)
```

---

### 4. SaveSlot 类 - 存档系统

#### ➕ 新增的字段

**`screenshot_path` - 存档截图路径**
```python
screenshot_path: Optional[str] = Field(
    None,
    description="存档截图路径（可选，用于可视化存档列表）"
)
```

#### 🔧 优化的字段

**`slot_id` - 添加了数值验证**
```python
slot_id: int = Field(..., ge=1, description="存档槽位 ID")
```

---

### 5. 新增的枚举类

**`NarrativePhase` - 剧情阶段枚举**
```python
class NarrativePhase(str, Enum):
    """剧情阶段枚举 - 用于控制叙事节奏"""
    INTRO = "intro"                      # 序章/开场
    RISING_ACTION = "rising_action"      # 发展/上升阶段
    CLIMAX = "climax"                    # 高潮
    RESOLUTION = "resolution"            # 结局/收尾
```

---

## 📊 字段变更对比表

### Character 类

| 字段 | 状态 | 说明 |
|------|------|------|
| `id` | ✅ 保留 | 无变化 |
| `name` | ✅ 保留 | 无变化 |
| `visual_traits` | ✅ 保留 | 无变化 |
| `base_img_ref` | ✅ 保留 | 优化了注释 |
| `stats` | ⚠️ 重新定义 | **仅用于关系型数值，严禁战斗属性** |
| `memory_buffer` | ➕ **新增** | **存储角色关键记忆** |
| `description` | ✅ 保留 | 无变化 |
| `personality` | ✅ 保留 | 无变化 |
| `background` | ✅ 保留 | 无变化 |
| `weight` | 🔧 优化 | 添加了数值范围验证 (0-100) |
| `related_characters` | 🔧 优化 | 优化了格式说明 |
| `related_events` | ✅ 保留 | 无变化 |

### GameState 类

| 字段 | 状态 | 说明 |
|------|------|------|
| `turn_count` | 🔧 优化 | 重新定义为"剧情节奏计数器" |
| `current_phase` | ➕ **新增** | **剧情阶段标记（intro/rising_action/climax/resolution）** |
| `current_location` | ✅ 保留 | 无变化 |
| `active_characters` | ✅ 保留 | 无变化 |
| `inventory` | ❌ 删除 | 重命名为 `key_items` |
| `key_items` | ➕ **新增** | **替代 inventory，仅存关键道具** |
| `story_context` | ✅ 保留 | 即时剧情上下文 |
| `narrative_summary` | ➕ **新增** | **全局剧情摘要，解决上下文限制** |
| `flags` | ✅ 保留 | 无变化 |
| `player_name` | ✅ 保留 | 无变化 |
| `timestamp` | ✅ 保留 | 无变化 |

### GameConfig 类

| 字段 | 状态 | 说明 |
|------|------|------|
| `visual_backend` | ✅ 保留 | 无变化 |
| `style_tags` | ✅ 保留 | 优化了说明 |
| `difficulty` | 🔧 优化 | 重新定义为"选项复杂度" |
| `auto_save` | ✅ 保留 | 无变化 |
| `text_speed` | 🔧 优化 | 添加了范围验证 (0.5-3.0) |
| `enable_voice` | ✅ 保留 | 无变化 |
| `narrative_style` | ➕ **新增** | **叙事风格偏好** |

---

## 🎯 核心改进点总结

### 1. 角色记忆系统 🧠
- **新增 `memory_buffer`** 让角色能够"记住"重要事件
- 解决 AI 在长对话中遗忘前期设定的问题

### 2. 剧情阶段控制 🎬
- **新增 `current_phase`** 实现三幕剧结构
- 帮助 AI 生成符合当前剧情阶段的内容

### 3. 全局摘要机制 📝
- **新增 `narrative_summary`** 压缩长期剧情信息
- 突破上下文窗口限制，支持长篇叙事

### 4. 关键道具系统 🔑
- **重命名 `inventory` → `key_items`**
- 明确只存储影响剧情的关键物品

### 5. 关系型数值规范 💕
- **严格限定 `stats`** 只用于情感/心理数值
- 移除所有战斗/RPG 相关概念

---

## 📚 使用示例

### 创建一个纯 VN 角色

```python
from src.models import Character

heroine = Character(
    id="char_heroine",
    name="樱",
    visual_traits={
        "hair_color": "粉色长发",
        "eye_color": "蓝色瞳孔",
        "clothing": "校服",
        "expression": "温柔的微笑"
    },
    stats={
        "affection": 50,      # 好感度
        "trust": 40,          # 信任度
        "intimacy": 30,       # 亲密度
        "stress": 15          # 压力值
    },
    memory_buffer=[
        "第一次在图书馆相遇",
        "玩家帮她捡起了掉落的书",
        "记得玩家喜欢草莓味的饮料"
    ],
    personality="温柔、善良、有些内向",
    background="转学生，似乎有不为人知的过去",
    weight=85
)
```

### 创建纯 VN 游戏状态

```python
from src.models import GameState

game = GameState(
    turn_count=25,
    current_phase="rising_action",  # 剧情发展阶段
    current_location="学校天台",
    active_characters=["char_heroine", "char_rival"],
    key_items=["樱送的手帕", "神秘的旧照片"],  # 仅关键道具
    narrative_summary="""
        你是一名转学到新学校的高中生。第一天就在图书馆遇见了温柔的樱，
        你们逐渐成为了朋友。但最近，你发现她似乎隐藏着某个秘密...
    """,
    story_context="樱约你来到天台，她说有重要的事情要告诉你...",
    flags={
        "met_heroine": True,
        "trust_threshold_reached": True,
        "route": "樱线"
    },
    player_name="阿尔文"
)
```

---

## ⚠️ 重要注意事项

### 1. 数据库兼容性
如果已有旧存档，需要进行数据迁移：
- `inventory` → `key_items` 字段重命名
- 为所有角色添加空的 `memory_buffer`
- 为所有游戏状态添加 `current_phase` 和 `narrative_summary`

### 2. API 调整
相关代码需要同步修改：
- `src/database.py` - 可能需要处理字段迁移
- `app.py` - UI 显示需要适配新字段
- 未来的剧情生成引擎需要利用新增字段

### 3. 建议的后续开发
1. 实现 `memory_buffer` 的自动管理机制
2. 实现 `narrative_summary` 的自动摘要生成
3. 基于 `current_phase` 调整 AI 生成策略
4. 开发关键道具影响剧情分支的系统

---

## ✅ 重构完成清单

- [x] Character 类添加 `memory_buffer` 字段
- [x] Character 类重新定义 `stats` 字段用途
- [x] GameState 类添加 `current_phase` 字段
- [x] GameState 类添加 `narrative_summary` 字段
- [x] GameState 类将 `inventory` 重命名为 `key_items`
- [x] GameConfig 类添加 `narrative_style` 字段
- [x] 所有字段添加详细的中文注释
- [x] 添加数值范围验证（`weight`, `text_speed` 等）
- [x] 优化示例数据（更贴近 VN 风格）
- [x] 移除所有 RPG/战斗相关的概念和术语

---

**重构完成！** 🎉

现在 `src/models.py` 已经完全适配纯剧情向 Visual Novel 的需求。




