"""
核心数据模型 - 纯剧情向 Visual Novel
使用 Pydantic 进行严格的数据验证

架构升级：支持双小说驱动（世界观小说 + 恋爱小说）和深度女主角建模
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class VisualBackend(str, Enum):
    """视觉生成后端枚举"""
    SILICONFLOW = "siliconflow"
    LOCAL_PONY = "local_pony"


class NarrativePhase(str, Enum):
    """剧情阶段枚举 - 用于控制叙事节奏"""
    INTRO = "intro"                      # 序章/开场
    RISING_ACTION = "rising_action"      # 发展/上升阶段
    CLIMAX = "climax"                    # 高潮
    RESOLUTION = "resolution"            # 结局/收尾


# ============================================================
# 双小说驱动系统 - The Knowledge Base
# ============================================================

class EventNode(BaseModel):
    """
    事件节点模型 - 用于结构化时间线节点
    提供更丰富的事件信息，支持因果关系追踪和逻辑推理
    """
    
    timestamp: str = Field(
        ...,
        description="""
        时间戳 - 灵活的时间表示方式
        示例：
          - "Year 1024" (公元纪年)
          - "Spring Era 5" (时代纪年)
          - "First Semester, Year 1" (学期表示)
          - "Month 3, Day 15" (月日表示)
          - "Ancient Times" (相对时间)
        
        用途：标识事件发生的绝对或相对时间位置，帮助 Logic Engine 理解时间顺序
        """
    )
    
    summary: str = Field(
        ...,
        description="""
        事件摘要 - 事件的主要描述
        应简洁明确地描述发生了什么，是时间线节点的核心信息
        
        示例：
          - "新生入学典礼：主角正式进入魔法学院"
          - "期中考试：魔法实战测试，主角展现非凡天赋"
          - "秋季祭典：各族学生齐聚，展现和平共处"
          - "古代封印松动：地下遗迹出现异常波动"
        
        用途：Logic Engine 可以快速了解事件内容，用于剧情生成和事件触发
        """
    )
    
    consequence: Optional[str] = Field(
        None,
        description="""
        因果影响 - 该事件导致的结果和影响（可选）
        描述此事件如何影响后续剧情发展，对 Logic Engine 至关重要
        
        示例：
          - "导致主角被分配到特殊班级"
          - "引发女主对主角的首次关注"
          - "成为后续冲突的导火索"
          - "暴露了某个角色的真实身份"
        
        用途：帮助 Logic Engine 理解事件之间的因果关系，生成连贯的后续剧情
        建议：对于关键转折点事件，务必填写此字段
        """
    )
    
    involved_factions: List[str] = Field(
        default_factory=list,
        description="""
        涉及的势力列表 - 哪些势力参与或受到此事件影响
        应引用 WorldLore.factions 中定义的势力名称
        
        示例：
          - ["光明议会", "暗影社团"]
          - ["贵族联盟", "自由战士"]
          - [] (如果事件不涉及特定势力)
        
        用途：
        1. 帮助 Logic Engine 判断哪些势力会对此事件有反应
        2. 用于生成相关势力的后续行为
        3. 支持复杂的多势力剧情线
        """
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="""
        事件标签列表 - 用于分类和检索事件
        可以用于标记事件类型、主题、重要性等
        
        示例：
          - ["War", "Magic", "Politics"] (战争、魔法、政治)
          - ["Romance", "School", "Daily"] (恋爱、校园、日常)
          - ["Crisis", "Action", "Mystery"] (危机、动作、悬疑)
          - ["Important", "Turning Point"] (重要、转折点)
        
        用途：
        1. Logic Engine 可以根据标签筛选相关事件
        2. 支持按主题生成剧情分支
        3. 便于事件库的管理和检索
        
        建议：每个事件包含 2-5 个标签
        """
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "Year 1024, Spring Semester",
                "summary": "新生入学典礼：主角正式进入魔法学院，被分配到火焰院",
                "consequence": "主角展现出罕见的魔法天赋，引起多位教师的注意，也为后续的试炼埋下伏笔",
                "involved_factions": ["光明议会", "暗影社团"],
                "tags": ["School", "Magic", "Important", "Turning Point"]
            }
        }


class WorldLore(BaseModel):
    """
    世界观知识库 - 从"世界观小说"提取的数据
    用途：为剧情生成提供世界观基础，确保生成内容符合设定的世界规则
    """
    
    rules: List[str] = Field(
        default_factory=list,
        description="""
        世界运作规则列表 - 定义该世界的物理规则、魔法系统、社会规则等。
        示例：
          - "魔法需要消耗精神力"
          - "吸血鬼无法接触阳光"
          - "时间旅行会产生悖论"
          - "超能力者必须经过政府登记"
        用途：让 AI 在生成剧情时遵守世界观设定，避免出现违背设定的情节
        """
    )
    
    locations: Dict[str, str] = Field(
        default_factory=dict,
        description="""
        关键地点字典 - 存储世界中的重要地点及其详细描述。
        格式：{"地点名称": "详细描述"}
        示例：
          {
            "魔法学院": "坐落在云端的古老学府，教授各类魔法知识",
            "迷雾森林": "充满危险的禁地，传说中藏有远古遗迹",
            "王都中央广场": "繁华的商业区，各族人民交流的场所"
          }
        用途：为场景生成提供详细背景，增强沉浸感
        """
    )
    
    timeline_nodes: List[EventNode] = Field(
        default_factory=list,
        description="""
        时间线节点列表 - 原著中的关键剧情发展节点，作为叙事参考。
        使用结构化的 EventNode 对象，提供更丰富的事件信息和因果关系。
        
        每个事件节点包含：
          - timestamp: 事件发生的时间
          - summary: 事件的主要描述
          - consequence: 该事件导致的因果影响（可选）
          - involved_factions: 涉及的势力列表
          - tags: 事件分类标签
        
        用途：
        1. 帮助 AI 把握整体剧情节奏，在合适的时机触发关键事件
        2. 理解事件之间的因果关系，生成连贯的后续剧情
        3. 根据涉及势力和标签筛选相关事件
        
        建议：
        - 按时间顺序排列所有事件节点
        - 对于关键转折点，务必填写 consequence 字段
        - 为每个事件添加适当的 tags 便于检索
        """
    )
    
    factions: Dict[str, str] = Field(
        default_factory=dict,
        description="""
        势力/组织字典 - 世界中存在的重要势力及其特征。
        格式：{"势力名称": "势力描述和立场"}
        示例：
          {
            "魔法师公会": "中立组织，维护魔法秩序",
            "贵族联盟": "保守派，反对平民学习魔法",
            "自由战士": "革命组织，追求平等"
          }
        用途：为角色提供背景归属，支撑复杂的剧情冲突
        """
    )
    
    lore_summary: str = Field(
        default="",
        description="世界观总览 - 用 1-2 段话概括整个世界的核心设定"
    )

    villian_type: str = Field(
        default="",
        description="""
        反派类型 - 世界中存在的反派类型"
        示例：
          - "黑暗势力：黑暗势力，追求权力和控制，拥有强大的力量和势力，但最终被正义力量击败"
          - "邪恶组织：邪恶组织，追求杀戮和破坏，做事不择手段，最后被全部消灭"
          - "个人反派：个人反派，智力极高，擅长各种阴谋诡计，跟主角之间存在误会，最终解开误会改邪归正"
        """
    )

    
    class Config:
        json_schema_extra = {
            "example": {
                "rules": [
                    "魔法需要通过咒语和手势施展",
                    "不同种族拥有不同的魔法亲和力",
                    "禁忌魔法会吸引魔物的注意"
                ],
                "locations": {
                    "星辰魔法学院": "建立于500年前的顶尖魔法学府，培养了无数传奇魔法师",
                    "古代遗迹": "隐藏在学院地下的神秘遗迹，据说封印着强大的力量"
                },
                "timeline_nodes": [
                    {
                        "timestamp": "Year 1024, Spring Semester",
                        "summary": "春季开学：新生入学典礼，主角正式进入魔法学院",
                        "consequence": "主角被分配到火焰院，开始接触学院的核心课程",
                        "involved_factions": ["光明议会"],
                        "tags": ["School", "Important"]
                    },
                    {
                        "timestamp": "Year 1024, Mid-Spring",
                        "summary": "第一次实战课：主角展现非凡的魔法天赋",
                        "consequence": "引起教师和同学的注意，成为学院内的焦点人物",
                        "involved_factions": [],
                        "tags": ["Magic", "School", "Turning Point"]
                    },
                    {
                        "timestamp": "Year 1024, Autumn Festival",
                        "summary": "秋季祭典：各族学生齐聚，主角与女主初次相识",
                        "consequence": "建立了跨种族的友谊，为后续剧情发展奠定基础",
                        "involved_factions": ["光明议会"],
                        "tags": ["Romance", "Social", "Important"]
                    },
                    {
                        "timestamp": "Year 1024, Winter Exam",
                        "summary": "冬季考核：主角面临重大抉择，必须在不同立场间做出选择",
                        "consequence": "选择将影响后续剧情走向和最终结局",
                        "involved_factions": ["光明议会", "暗影社团"],
                        "tags": ["Crisis", "Politics", "Turning Point"]
                    }
                ],
                "factions": {
                    "光明议会": "学院的管理机构，主张和平共处",
                    "暗影社团": "神秘的学生组织，研究禁忌魔法"
                },
                "lore_summary": "这是一个魔法与科技共存的世界，不同种族经历了漫长的战争后终于走向和平。魔法学院成为各族交流的桥梁，但古老的威胁正在苏醒...",
                "villian_type": "黑暗势力：黑暗势力，追求权力和控制，拥有强大的力量和势力，但最终被正义力量击败"
            }
        }


class RomanceScript(BaseModel):
    """
    恋爱剧本知识库 - 从"恋爱小说"提取的数据
    用途：为角色互动和情感发展提供范例和模板，确保恋爱线的质量和深度
    """
    
    interaction_events: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="""
        互动事件列表 - 原著中男女主发生的关键事件记录。
        每个事件包含：
          - event_name: 事件名称
          - description: 事件详细描述
          - emotional_shift: 情感转折（如：从陌生到好奇，从误会到理解）
          - affection_change: 好感度变化 (+10, -5 等)
          - key_dialogue: 关键对话片段
        
        示例：
        {
          "event_name": "雨中邂逅",
          "description": "女主忘带伞，男主分享了自己的伞",
          "emotional_shift": "从陌生到心动",
          "affection_change": +15,
          "key_dialogue": "谢谢你...其实我不介意淋雨的。"
        }
        
        用途：为 AI 生成类似的高质量互动事件提供模板和灵感
        """
    )
    
    dialogue_examples: List[str] = Field(
        default_factory=list,
        description="""
        典型对话范例列表 - 原著女主的典型台词，用于 Few-Shot 学习。
        示例：
          - "笨蛋...我才没有担心你呢！"（傲娇型）
          - "如果是你的话...我愿意相信。"（信任建立）
          - "为什么...为什么要对我这么好？"（情感困惑）
        
        用途：让 AI 学习女主的说话风格，保持角色一致性
        建议：包含 20-50 条代表性台词，涵盖不同情感状态
        """
    )
    
    relationship_stages: List[str] = Field(
        default_factory=list,
        description="""
        感情发展阶段定义 - 描述恋爱关系从初识到结局的标准流程。
        示例：
          - "相识：初次见面，留下印象"
          - "好奇：开始关注对方的行为"
          - "好感：产生好感，但未察觉"
          - "自觉：意识到自己的感情"
          - "误会：因误解产生隔阂"
          - "和解：化解误会，关系升温"
          - "告白：表达真心"
          - "交往：正式确立关系"
          - "深化：经历考验，感情深化"
          - "结局：迎来圆满结局或分离"
        
        用途：帮助 Logic Engine 判断当前处于哪个阶段，决定下一步剧情方向
        """
    )
    
    emotional_triggers: Dict[str, str] = Field(
        default_factory=dict,
        description="""
        情感触发器字典 - 定义哪些行为会触发女主的特定情感反应。
        格式：{"玩家行为": "女主情感反应"}
        示例：
          {
            "送礼物": "惊喜并感动，好感度提升",
            "约会迟到": "失望甚至生气，好感度下降",
            "保护她": "感到被重视，信任度大幅提升",
            "忽视她": "感到被冷落，可能触发负面剧情"
          }
        
        用途：让 AI 能够合理地模拟女主对玩家行为的反应
        """
    )
    
    romance_summary: str = Field(
        default="",
        description="恋爱线总览 - 用 1-2 段话概括原著恋爱线的核心情节和情感基调,但不要暗示最终最终两人感情的结局"
    )

    possible_ending: List[str] = Field(
        default_factory=list,
        description="""
        可能的结局列表 - 原著中可能的结局列表"
        示例：
        {
          - "圆满结局：两人最终走到一起"
          - "悲剧结局：因误会分离"
          - "开放结局：留下悬念，让玩家自行想象"
        }
        用途：帮助 Logic Engine 判断当前处于哪个阶段，决定下一步剧情方向
        """
    )

    class Config:
        json_schema_extra = {
            "example": {
                "interaction_events": [
                    {
                        "event_name": "图书馆初遇",
                        "description": "在图书馆中，女主的书掉落一地，男主帮忙捡起",
                        "emotional_shift": "从戒备到感谢",
                        "affection_change": 5,
                        "key_dialogue": "谢谢...你真是个温柔的人。"
                    },
                    {
                        "event_name": "屋顶的秘密",
                        "description": "女主在天台哭泣，男主倾听她的烦恼",
                        "emotional_shift": "从封闭到信任",
                        "affection_change": 20,
                        "key_dialogue": "我从没对别人说过这些...你是第一个。"
                    }
                ],
                "dialogue_examples": [
                    "你这个笨蛋...我才没有在意呢！",
                    "如果是你的话，我想我可以试着相信。",
                    "不要离开我...好吗？"
                ],
                "relationship_stages": [
                    "初识：图书馆偶遇",
                    "好感：开始期待再次相遇",
                    "自觉：意识到自己的心意",
                    "告白：勇敢表达感情",
                    "交往：成为恋人"
                ],
                "emotional_triggers": {
                    "送她喜欢的书": "非常开心，好感度+15",
                    "记住她说过的话": "感动，信任度+10",
                    "在她困难时伸出援手": "深深感激，关系突破"
                },
                "romance_summary": "这是一个从误解到理解，从陌生到深爱的故事。女主最初封闭内心，但在男主的温柔陪伴下逐渐打开心扉，最终两人跨越障碍走到一起。但不要暗示最终最终两人感情的结局",
                "possible_ending": [
                    "圆满结局：两人最终走到一起",
                    "悲剧结局：因误会分离",
                    "开放结局：留下悬念，让玩家自行想象"
                ]
            }
        }


class Character(BaseModel):
    """角色数据模型 - Visual Novel 专用"""
    id: str = Field(..., description="角色唯一标识符")
    name: str = Field(..., description="角色名称")
    
    visual_traits: Dict[str, str] = Field(
        default_factory=dict,
        description="视觉特征，用于 Flux 提示词生成（如发色、瞳色、服装等）"
    )
    base_img_ref: Optional[str] = Field(
        None,
        description="用于 PuLID 的参考图 URL，保持角色立绘风格一致性"
    )
    
    # ===== 关系型数值（严格用于剧情，非战斗） =====
    stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="""
        关系型数值字典 - 仅用于存储影响剧情走向的情感/心理数值。
        推荐字段：
          - affection (好感度): 0-100，影响角色对玩家的态度和剧情分支
          - trust (信任度): 0-100，影响角色是否愿意透露秘密
          - dominance (支配度): -100 到 100，角色在关系中的主导程度
          - stress (压力值): 0-100，影响角色的情绪稳定性和行为
          - intimacy (亲密度): 0-100，关系深度指标
        
        ⚠️ 严禁包含战斗数值（如 HP、MP、攻击力、防御力等）
        """
    )
    
    # ===== 角色记忆与背景 =====
    memory_buffer: List[str] = Field(
        default_factory=list,
        description="""
        角色记忆缓冲区 - 存储该角色经历过的关键事件摘要。
        用途：保持剧情连贯性，让 AI 记住角色的重要经历。
        示例：["记得玩家在雨中送过伞", "曾在咖啡厅与玩家约会", "知道玩家的秘密"]
        建议：每个摘要不超过 50 字，保留最近 20-30 条重要记忆
        """
    )
    
    description: str = Field(
        default="",
        description="角色外貌与性格的概括描述"
    )
    personality: str = Field(
        default="",
        description="角色性格特质（如：温柔、傲娇、腹黑、天然呆等）"
    )
    background: str = Field(
        default="",
        description="角色背景故事，用于为角色的决定和行为提供动机参考"
    )
    
    # ===== 关系网络 =====
    weight: int = Field(
        default=0,
        ge=0,
        le=100,
        description="角色权重 (0-100)，用于判断该角色的行为对后续剧情走向的影响程度"
    )
    related_characters: List[Dict[str, str]] = Field(
        default_factory=list,
        description="""
        与该角色相关联的角色关系列表。
        格式：[{"character_id": "char_002", "relationship": "青梅竹马"}, ...]
        关系类型示例：朋友、恋人、竞争对手、家人、师徒等
        """
    )
    related_events: List[str] = Field(
        default_factory=list,
        description="与该角色相关的事件 ID 列表，用于追踪角色的剧情线"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "char_001",
                "name": "艾莉娅",
                "visual_traits": {
                    "hair_color": "银色长发",
                    "eye_color": "紫色瞳孔",
                    "clothing": "白色连衣裙",
                    "accessories": "星形耳环"
                },
                "base_img_ref": "https://example.com/character_ref.png",
                "stats": {
                    "affection": 50,
                    "trust": 40,
                    "dominance": -10,
                    "stress": 20,
                    "intimacy": 30
                },
                "memory_buffer": [
                    "记得玩家在雨中送过伞",
                    "第一次在图书馆相遇",
                    "玩家帮她找回了重要的项链"
                ],
                "description": "来自异世界的神秘少女，温柔而优雅",
                "personality": "温柔、内敛、有些神秘",
                "background": "曾是异世界的贵族小姐，因某种原因来到人间",
                "weight": 80,
                "related_characters": [
                    {"character_id": "char_002", "relationship": "好友"}
                ],
                "related_events": ["event_001", "event_003"]
            }
        }


# ============================================================
# 深度女主角建模 - The Heroine
# ============================================================

class Heroine(Character):
    """
    女主角深度模型 - 继承自基础 Character 类，扩展恋爱向功能
    
    与普通 Character 的区别：
    1. 拥有更详细的心理侧写
    2. 具有明确的说话风格和台词模式
    3. 追踪当前所处的恋爱阶段
    4. 拥有独立于全局剧情的专属记忆
    """
    
    # ===== 深度心理建模 =====
    psychological_profile: str = Field(
        default="",
        description="""
        深度心理侧写 - 从恋爱小说中提取的女主深层心理特征。
        应包含：
          - 核心价值观（重视什么，害怕什么）
          - 情感模式（如何表达情感，如何应对冲突）
          - 过往创伤或经历对性格的影响
          - 对恋爱的态度和期待
          - 内心矛盾和成长方向
        
        示例：
        "表面上独立坚强，实际上内心脆弱。因为童年被抛弃的经历，她害怕依赖他人，
        总是用冷漠的态度保护自己。她渴望被理解，但又恐惧敞开心扉后的再次受伤。
        在恋爱中，她会表现出矛盾的行为——一边推开对方，一边暗自期待对方的坚持。"
        
        用途：让 AI 能够生成深层次的、符合人物心理的对话和行为
        """
    )
    
    # ===== 语言风格建模 =====
    speech_pattern: str = Field(
        default="",
        description="""
        说话风格描述 - 详细描述女主的语言习惯和表达模式。
        应包含：
          - 语气特征（温柔、直接、傲娇、神秘等）
          - 惯用词汇或口头禅
          - 句式特点（短句、长句、反问句、省略句等）
          - 不同情感状态下的语言变化
        
        示例：
        "典型的傲娇说话方式。习惯用'才不是呢'、'笨蛋'等词。当害羞时会结巴，
        当生气时语速加快。在表达关心时会采用反问句或否定句来掩饰真实情感。
        例如：'我才不是担心你呢！只是...只是路过而已！'
        当情感深入后，会偶尔展现出温柔的一面，使用更直接的表达。"
        
        用途：确保 AI 生成的对话符合女主的语言风格，保持角色一致性
        """
    )
    
    # ===== 恋爱进度追踪 =====
    current_romance_stage: str = Field(
        default="初识",
        description="""
        当前恋爱阶段 - 标记女主与玩家的关系当前处于哪个阶段。
        应与 RomanceScript.relationship_stages 中定义的阶段对应。
        
        示例："初识" / "好感" / "自觉" / "告白" / "交往" 等
        
        用途：
        1. 帮助 Logic Engine 判断当前应该生成什么类型的剧情
        2. 决定女主对玩家行为的反应强度
        3. 控制剧情推进的节奏（不会跳过必要阶段）
        """
    )
    
    # ===== 专属记忆系统 =====
    exclusive_memory: List[str] = Field(
        default_factory=list,
        description="""
        女主专属记忆 - 仅属于女主角的记忆，区别于全局剧情记忆。
        
        与 Character.memory_buffer 的区别：
        - memory_buffer: 客观事件记忆（"玩家送过伞"）
        - exclusive_memory: 女主的主观感受和内心独白（"那天他为我撑伞时，我的心跳得好快"）
        
        示例：
          - "第一次见到他时，我就觉得他的眼神很温柔"
          - "他记得我喜欢草莓味，这让我很开心，虽然我没有表现出来"
          - "当他说要保护我时，我的心里涌起了从未有过的安心感"
          - "我开始期待每天能见到他...这是恋爱的感觉吗？"
        
        用途：
        1. 为内心独白和私密对话提供素材
        2. 展现女主的情感成长轨迹
        3. 支撑更深层次的心理描写
        
        建议：保留最重要的 15-20 条情感记忆
        """
    )
    
    # ===== 恋爱特质 =====
    love_language: str = Field(
        default="",
        description="""
        爱的语言 - 女主表达和接收爱意的方式。
        基于"五种爱的语言"理论：
          1. 肯定的言辞（喜欢听赞美和鼓励）
          2. 精心时刻（重视高质量的陪伴时间）
          3. 接受礼物（礼物是爱的象征）
          4. 服务的行动（通过行动表达关心）
          5. 身体的接触（拥抱、牵手等）
        
        示例："她最看重精心时刻和肯定的言辞。喜欢两个人安静地待在一起，
        享受彼此的陪伴。真诚的赞美和鼓励能让她感到被重视。"
        
        用途：帮助 AI 生成更有针对性的互动建议，提高玩家攻略成功率
        """
    )
    
    emotional_boundaries: List[str] = Field(
        default_factory=list,
        description="""
        情感边界列表 - 女主在恋爱中的底线和敏感点。
        示例：
          - "不要提及她的家庭（触发负面情绪）"
          - "不要在她朋友面前过于亲密（会感到尴尬）"
          - "不要强迫她做不想做的事（会失去信任）"
          - "不要忽视她的感受（会感到被轻视）"
        
        用途：防止 AI 生成破坏角色形象或引发负面反应的内容
        """
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "heroine_001",
                "name": "艾莉娅",
                "visual_traits": {
                    "hair_color": "银色长发",
                    "eye_color": "紫色瞳孔",
                    "clothing": "白色连衣裙",
                    "expression": "温柔中带着一丝忧郁"
                },
                "stats": {
                    "affection": 50,
                    "trust": 45,
                    "intimacy": 30,
                    "stress": 25
                },
                "memory_buffer": [
                    "在图书馆第一次相遇",
                    "玩家帮她找回了项链",
                    "一起在天台看星星"
                ],
                "psychological_profile": """
                    表面温柔优雅，实则内心孤独。作为异界来客，她始终有一种疏离感，
                    害怕与人建立深层联系，因为她知道自己终将离开。她渴望被理解，
                    但又害怕当别人知道她的真实身份后会疏远她。在恋爱中，她会表现出
                    犹豫和矛盾——既想靠近，又想保持距离。
                """,
                "speech_pattern": """
                    说话温柔而文雅，带有一丝古典气质。常用'呢'、'吗'等语气词。
                    当害羞时会用'那个...'开头。情绪激动时会说得更快，但依然保持礼貌。
                    例如：'你...你怎么会知道这些的？我明明没有告诉任何人...'
                """,
                "current_romance_stage": "好感",
                "exclusive_memory": [
                    "第一次见到他时，他的笑容让我想起了家乡的温暖",
                    "他毫不犹豫地帮助我时，我感到了久违的安心",
                    "每次和他在一起，我都会忘记自己的身份...这样真的好吗？"
                ],
                "love_language": "她重视精心时刻和服务的行动。喜欢两人安静地待在一起，也会被对方的体贴行动深深打动。",
                "emotional_boundaries": [
                    "不要追问她的过去（会触发痛苦回忆）",
                    "不要在她准备好之前强迫表白（会吓到她）",
                    "不要轻视她的感受（会让她封闭内心）"
                ]
            }
        }


class GameState(BaseModel):
    """
    游戏状态数据模型 - Visual Novel 专用
    
    架构升级：集成双小说知识库，支持深度剧情生成
    """
    
    # ===== 双小说知识库引用 =====
    world_lore: Optional[WorldLore] = Field(
        default=None,
        description="""
        世界观知识库实例 - 存储从"世界观小说"提取的所有设定数据。
        Logic Engine 在生成剧情时会查询此对象，确保内容符合世界观。
        
        使用场景：
        - 生成场景描述时，查询 locations 获取地点信息
        - 触发事件时，查询 timeline_nodes 确保时机合理
        - 判断角色行为时，查询 rules 确保不违背世界规则
        - 在生成故事反派时，查询 villian_type 确定反派类型
        """
    )
    
    romance_script: Optional[RomanceScript] = Field(
        default=None,
        description="""
        恋爱剧本知识库实例 - 存储从"恋爱小说"提取的互动模板和情感数据。
        Logic Engine 在生成角色互动时会参考此对象，确保恋爱线的质量。
        
        使用场景：
        - 生成女主对话时，参考 dialogue_examples 学习说话风格
        - 触发互动事件时，参考 interaction_events 设计高质量剧情
        - 判断关系进展时，查询 relationship_stages 确定当前阶段
        - 玩家做出选择时，查询 emotional_triggers 决定女主反应
        - 在生成最终结局时，查询 possible_ending 确定最终结局
        """
    )
    
    # ===== 剧情进度与节奏控制 =====
    turn_count: int = Field(
        default=0,
        ge=0,
        description="剧情节奏计数器 - 记录当前是第几个回合/场景，用于控制剧情推进速度"
    )
    
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
    
    # ===== 场景与角色状态 =====
    current_location: str = Field(
        default="starting_point",
        description="当前场景位置（如：咖啡厅、学校屋顶、公园等）"
    )
    
    active_characters: List[str] = Field(
        default_factory=list,
        description="当前场景中出现的角色 ID 列表，用于判断谁在场、谁可以说话"
    )
    
    # ===== 关键道具系统 =====
    key_items: List[str] = Field(
        default_factory=list,
        description="""
        关键道具列表 - 仅存储影响剧情分支的重要物品。
        示例：["定情信物", "未寄出的信", "神秘钥匙", "旧照片"]
        
        ⚠️ 不存储消耗品（如药水、食物等），这是纯剧情向 VN，非 RPG
        """
    )
    
    # ===== 剧情上下文管理 =====
    story_context: str = Field(
        default="",
        description="当前场景的即时剧情上下文（最近 3-5 个回合的内容）"
    )
    
    narrative_summary: str = Field(
        default="",
        description="""
        全局剧情摘要 - 用于解决长篇剧情的上下文窗口限制。
        记录整体故事的关键发展、重要选择和结果，防止 AI 在 50 回合后忘记前期设定。
        建议：每 10-20 回合更新一次，保持在 500-1000 字以内。
        """
    )
    
    # ===== 剧情分支标志位 =====
    flags: Dict[str, Any] = Field(
        default_factory=dict,
        description="""
        剧情标志位字典 - 用于分支剧情判断。
        示例：
          - met_heroine: True (是否见过女主)
          - confession_accepted: False (告白是否被接受)
          - ending_route: "艾莉娅线" (当前走向哪条路线)
          - secret_revealed: True (秘密是否已揭露)
        """
    )
    
    # ===== 玩家信息 =====
    player_name: str = Field(
        default="旅行者",
        description="玩家/主角的名称"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="状态保存时间戳"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "world_lore": {
                    "rules": ["魔法需要咒语施展", "不同种族有不同魔法亲和"],
                    "locations": {
                        "魔法学院": "培养魔法师的学府",
                        "古代遗迹": "封印着强大力量"
                    },
                    "timeline_nodes": [
                        {
                            "timestamp": "Year 1024, Spring",
                            "summary": "开学典礼：新生入学",
                            "consequence": "主角开始学院生活",
                            "involved_factions": [],
                            "tags": ["School"]
                        }
                    ],
                    "lore_summary": "魔法与现实交织的世界..."
                },
                "romance_script": {
                    "interaction_events": [
                        {
                            "event_name": "图书馆初遇",
                            "emotional_shift": "从陌生到好奇",
                            "affection_change": 5
                        }
                    ],
                    "dialogue_examples": ["你这个笨蛋...", "如果是你的话..."],
                    "relationship_stages": ["初识", "好感", "自觉", "告白", "交往"],
                    "romance_summary": "从误解到深爱的故事..."
                },
                "turn_count": 42,
                "current_phase": "rising_action",
                "current_location": "学校天台",
                "active_characters": ["char_001", "char_002"],
                "key_items": ["艾莉娅的项链", "神秘的旧照片"],
                "story_context": "艾莉娅终于向你吐露了她的秘密...",
                "narrative_summary": "你是一名普通的高中生，某天遇见了神秘转学生艾莉娅。经过数周相处，你们的关系逐渐亲密，但她似乎隐藏着不为人知的秘密...",
                "flags": {
                    "met_heroine": True,
                    "trust_level_reached": 3,
                    "route": "艾莉娅线",
                    "secret_revealed": False
                },
                "player_name": "阿尔文",
                "timestamp": "2025-12-05T15:30:00"
            }
        }


class GameConfig(BaseModel):
    """游戏配置数据模型"""
    
    # ===== 视觉生成配置 =====
    visual_backend: VisualBackend = Field(
        default=VisualBackend.SILICONFLOW,
        description="视觉生成后端选择（SiliconFlow 或本地 Pony）"
    )
    
    style_tags: List[str] = Field(
        default_factory=list,
        description="""
        风格标签列表，用于图像生成风格控制。
        示例：["anime", "visual_novel", "soft_lighting", "detailed"]
        """
    )
    
    # ===== 游戏体验配置 =====
    difficulty: str = Field(
        default="normal",
        description="""
        游戏难度 - 在 VN 中影响选项的复杂度和结局达成难度。
        可选值：easy (明确提示), normal (适度提示), hard (无提示)
        """
    )
    
    auto_save: bool = Field(
        default=True,
        description="是否启用自动保存（每 N 个回合自动保存一次）"
    )
    
    text_speed: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="文本显示速度倍率（0.5 = 慢速, 1.0 = 正常, 2.0 = 快速）"
    )
    
    enable_voice: bool = Field(
        default=False,
        description="是否启用角色语音（TTS）"
    )
    
    # ===== 叙事控制 =====
    narrative_style: str = Field(
        default="romantic",
        description="""
        叙事风格偏好，影响 AI 生成内容的基调。
        可选：romantic (浪漫), dramatic (戏剧性), slice_of_life (日常), mystery (悬疑)
        """
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "visual_backend": "siliconflow",
                "style_tags": ["anime", "visual_novel", "soft_colors", "detailed"],
                "difficulty": "normal",
                "auto_save": True,
                "text_speed": 1.0,
                "enable_voice": False,
                "narrative_style": "romantic"
            }
        }


class SaveSlot(BaseModel):
    """存档槽数据模型"""
    slot_id: int = Field(..., ge=1, description="存档槽位 ID")
    timestamp: datetime = Field(..., description="保存时间戳")
    game_state: GameState = Field(..., description="完整的游戏状态数据")
    preview_text: str = Field(
        default="",
        description="存档预览文本（显示在存档列表中）"
    )
    screenshot_path: Optional[str] = Field(
        None,
        description="存档截图路径（可选，用于可视化存档列表）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot_id": 1,
                "timestamp": "2025-12-05T15:30:00",
                "game_state": {},
                "preview_text": "发展阶段 - 学校天台 - 回合42",
                "screenshot_path": "cache/saves/slot_1_preview.png"
            }
        }
