"""
ETL Pipeline - 数据提取管道
Phase 2: 从清洗后的 TXT 小说提取结构化数据

架构：Map-Reduce
- Map: 并行处理文本块，提取碎片信息
- Reduce: 聚合碎片数据，合成完整结构

依赖：
- OpenAI AsyncClient (连接 SiliconFlow)
- asyncio (并发控制)
- Pydantic (数据验证)
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# 添加项目根目录到 Python 路径（支持直接运行脚本）
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# 加载 .env 文件
from dotenv import load_dotenv
env_path = _project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

# 导入数据模型
from src.models import (
    WorldLore,
    RomanceScript,
    EventNode,
    Heroine
)


# ============================================================
# 配置常量
# ============================================================

# SiliconFlow API 配置
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# 从环境变量读取 API Key（在运行时检查）
def get_api_key() -> str:
    """获取 API Key"""
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "请设置环境变量 SILICONFLOW_API_KEY 或 OPENAI_API_KEY"
        )
    return api_key

# 并发控制
MAX_CONCURRENT_REQUESTS = 8  # 并发请求数限制

# Token 估算（1 token ≈ 4 字符，保守估计）
TOKEN_PER_CHAR = 0.25
CHUNK_SIZE_TOKENS = 3000  # 每块约 3000 tokens
OVERLAP_TOKENS = 500  # 重叠 500 tokens
CHUNK_SIZE_CHARS = int(CHUNK_SIZE_TOKENS / TOKEN_PER_CHAR)  # 约 12000 字符
OVERLAP_CHARS = int(OVERLAP_TOKENS / TOKEN_PER_CHAR)  # 约 2000 字符


# ============================================================
# 中间数据模型（用于 Map 步骤）
# ============================================================

class PartialWorldLore(BaseModel):
    """世界观提取的碎片数据（单个 Chunk 的结果）"""
    rules: List[str] = Field(default_factory=list)
    locations: Dict[str, str] = Field(default_factory=dict)
    timeline_nodes: List[EventNode] = Field(default_factory=list)
    factions: Dict[str, str] = Field(default_factory=dict)
    lore_summary: str = ""
    villian_type: str = ""  # 关键：必须保留


class PartialRomanceData(BaseModel):
    """恋爱小说提取的碎片数据（单个 Chunk 的结果）"""
    interaction_events: List[Dict[str, Any]] = Field(default_factory=list)
    dialogue_snippets: List[str] = Field(
        default_factory=list,
        description="女主台词原句（原始素材）"
    )
    psychology_clues: List[str] = Field(
        default_factory=list,
        description="心理描写片段（原始素材）"
    )
    relationship_stages: List[str] = Field(default_factory=list)
    emotional_triggers: Dict[str, str] = Field(default_factory=dict)
    possible_ending: List[str] = Field(default_factory=list)  # 关键：必须保留
    romance_summary: str = ""


# ============================================================
# 1. NovelLoader - 文本切片器
# ============================================================

class NovelLoader:
    """
    文本切片器
    将长文本按 Token 窗口切分，保持上下文连贯性
    """
    
    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE_CHARS,
        overlap: int = OVERLAP_CHARS
    ):
        """
        初始化切片器
        
        Args:
            chunk_size: 每块的字符数（约对应 3000 tokens）
            overlap: 重叠字符数（约对应 500 tokens）
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def load_file(self, file_path: Path) -> str:
        """
        加载文本文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容（字符串）
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"[NovelLoader] 已加载文件: {file_path.name} ({len(content)} 字符)")
        return content
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        将文本切分为多个块
        
        Args:
            text: 原始文本
            
        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # 计算当前块的结束位置
            end = min(start + self.chunk_size, text_length)
            
            # 提取当前块
            chunk = text[start:end]
            chunks.append(chunk)
            
            # 如果还没到文件末尾，移动到下一个块（考虑重叠）
            if end < text_length:
                start = end - self.overlap
            else:
                break
        
        print(f"[NovelLoader] 文本已切分为 {len(chunks)} 个块")
        print(f"  每块大小: ~{self.chunk_size} 字符 (~{CHUNK_SIZE_TOKENS} tokens)")
        print(f"  重叠大小: {self.overlap} 字符 (~{OVERLAP_TOKENS} tokens)")
        
        return chunks


# ============================================================
# 2. DeepSeekExtractor - 核心提取器（Map Step）
# ============================================================

class DeepSeekExtractor:
    """
    核心提取器 - Map 步骤的核心组件
    
    使用 DeepSeek V3 模型从文本块中提取结构化信息
    支持异步并发处理
    """
    
    def __init__(self, api_key: str, base_url: str = BASE_URL, model: str = MODEL_NAME):
        """
        初始化提取器
        
        Args:
            api_key: SiliconFlow API 密钥
            base_url: API 基础 URL
            model: 模型名称
        """
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async def _call_api(self, system_prompt: str, user_prompt: str, max_retries: int = 3) -> str:
        """
        调用 DeepSeek API（带并发控制和重试）
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数
            
        Returns:
            AI 响应文本
        """
        async with self.semaphore:  # 并发控制
            for attempt in range(max_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,  # 降低温度，提高准确性
                        max_tokens=4000,  # 允许较长的输出
                    )
                    
                    content = response.choices[0].message.content
                    if content:
                        return content.strip()
                    else:
                        raise ValueError("API 返回空内容")
                
                except Exception as e:
                    if attempt == max_retries - 1:
                        print(f"[警告] API 调用失败（已重试 {max_retries} 次）: {e}")
                        raise
                    await asyncio.sleep(2 ** attempt)  # 指数退避
        
        raise RuntimeError("API 调用失败")
    
    async def extract_world_chunk(self, text: str, chunk_index: int) -> PartialWorldLore:
        """
        从世界观小说文本块提取信息
        
        Args:
            text: 文本块内容
            chunk_index: 块索引（用于日志）
            
        Returns:
            PartialWorldLore 对象
        """
        system_prompt = """你是一个专业的世界观数据提取专家。
你的任务是从小说文本中提取世界观相关的结构化信息。

输出要求：
1. 必须使用 JSON 格式
2. 严格按照提供的 JSON Schema 输出
3. timeline_nodes 中的每个事件必须包含 timestamp, summary, consequence, involved_factions, tags 字段
4. 如果没有相关信息，使用空列表 [] 或空字符串 ""
5. villian_type 字段必须尝试提取，即使文本中没有明确提及，也要根据反派行为特征进行推测

输出格式：
{
  "rules": ["规则1", "规则2"],
  "locations": {"地点名": "描述"},
  "timeline_nodes": [
    {
      "timestamp": "时间戳（如 Year 1024）",
      "summary": "事件摘要",
      "consequence": "因果影响（可选）",
      "involved_factions": ["势力1"],
      "tags": ["标签1", "标签2"]
    }
  ],
  "factions": {"势力名": "描述"},
  "lore_summary": "世界观摘要",
  "villian_type": "反派类型描述（如果有）"
}"""

        user_prompt = f"""请从以下小说文本中提取世界观信息：

{text}

要求：
1. 提取所有世界规则（魔法规则、物理规则、社会规则等）
2. 提取关键地点及其描述
3. 提取时间线事件（使用 EventNode 格式，必须包含所有字段）
4. 提取势力/组织及其立场
5. 提取反派类型特征（如果文本中提及反派）
6. 生成简短的世界观摘要

请以 JSON 格式输出，确保所有字段都存在。"""

        # 重试机制：最多重试 2 次
        max_retries = 2
        last_error = None
        last_json_text = None
        
        for attempt in range(max_retries):
            try:
                response_text = await self._call_api(system_prompt, user_prompt)
                
                # 提取并尝试解析 JSON
                json_text = self._extract_json_from_response(response_text)
                last_json_text = json_text
                
                # 使用带重试的 JSON 解析
                data = self._parse_json_with_retry(json_text, max_retries=2)
                
                if data is None:
                    raise json.JSONDecodeError("JSON 解析失败", json_text, 0)
                
                # 转换为 PartialWorldLore
                partial_lore = PartialWorldLore(**data)
                
                print(f"[Extractor] 世界观块 {chunk_index} 提取完成: "
                      f"{len(partial_lore.rules)} 规则, "
                      f"{len(partial_lore.locations)} 地点, "
                      f"{len(partial_lore.timeline_nodes)} 事件, "
                      f"{len(partial_lore.factions)} 势力")
                
                return partial_lore
            
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[警告] 世界观块 {chunk_index} 提取失败（尝试 {attempt + 1}/{max_retries}），正在重试...")
                    await asyncio.sleep(1)  # 等待 1 秒后重试
                else:
                    # 最后一次尝试也失败，保存错误日志
                    error_msg = f"[错误] 世界观块 {chunk_index} 提取失败: {e}"
                    print(error_msg)
                    self._save_error_log(chunk_index, "world", last_json_text, str(e))
        
        # 所有重试都失败，返回空对象
        return PartialWorldLore()
    
    async def extract_romance_chunk(self, text: str, chunk_index: int) -> PartialRomanceData:
        """
        从恋爱小说文本块提取信息
        
        Args:
            text: 文本块内容
            chunk_index: 块索引（用于日志）
            
        Returns:
            PartialRomanceData 对象
        """
        system_prompt = """你是一个专业的恋爱小说数据提取专家。
你的任务是从恋爱小说文本中提取角色互动和情感发展的结构化信息。

重要说明：
- dialogue_snippets: 提取女主说的原句（逐字提取，不要修改）
- psychology_clues: 提取描述女主心理状态的文本片段（原文）
- 这一步只收集素材，不生成最终的 profile
- possible_ending 字段必须尝试预测可能的结局走向

输出格式：
{
  "interaction_events": [
    {
      "event_name": "事件名",
      "description": "描述",
      "emotional_shift": "情感转折",
      "affection_change": 10,
      "key_dialogue": "关键对话"
    }
  ],
  "dialogue_snippets": ["女主台词原句1", "女主台词原句2"],
  "psychology_clues": ["心理描写片段1", "心理描写片段2"],
  "relationship_stages": ["阶段1", "阶段2"],
  "emotional_triggers": {"行为": "反应"},
  "possible_ending": ["结局1", "结局2"],
  "romance_summary": "摘要"
}"""

        user_prompt = f"""请从以下恋爱小说文本中提取信息：

{text}

要求：
1. 提取关键互动事件（必须包含所有字段）
2. 提取女主的原句台词（dialogue_snippets）- 逐字提取，不要修改
3. 提取描述女主心理状态的文本片段（psychology_clues）- 保留原文
4. 识别感情发展阶段
5. 提取情感触发器映射
6. 预测可能的结局走向（possible_ending）
7. 生成简短的恋爱线摘要（但不要暗示最终结局）

注意：
- dialogue_snippets 和 psychology_clues 是原始素材，用于后续合成深度人设
- 不要在这步生成最终的 psychological_profile 或 speech_pattern
- possible_ending 必须包含（即使只是推测）

请以 JSON 格式输出。"""

        # 重试机制：最多重试 2 次
        max_retries = 2
        last_error = None
        last_json_text = None
        
        for attempt in range(max_retries):
            try:
                response_text = await self._call_api(system_prompt, user_prompt)
                
                # 提取并尝试解析 JSON
                json_text = self._extract_json_from_response(response_text)
                last_json_text = json_text
                
                # 使用带重试的 JSON 解析
                data = self._parse_json_with_retry(json_text, max_retries=2)
                
                if data is None:
                    raise json.JSONDecodeError("JSON 解析失败", json_text, 0)
                
                # 转换为 PartialRomanceData
                partial_data = PartialRomanceData(**data)
                
                print(f"[Extractor] 恋爱块 {chunk_index} 提取完成: "
                      f"{len(partial_data.interaction_events)} 事件, "
                      f"{len(partial_data.dialogue_snippets)} 台词, "
                      f"{len(partial_data.psychology_clues)} 心理线索, "
                      f"{len(partial_data.possible_ending)} 可能结局")
                
                return partial_data
            
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[警告] 恋爱块 {chunk_index} 提取失败（尝试 {attempt + 1}/{max_retries}），正在重试...")
                    await asyncio.sleep(1)  # 等待 1 秒后重试
                else:
                    # 最后一次尝试也失败，保存错误日志
                    error_msg = f"[错误] 恋爱块 {chunk_index} 提取失败: {e}"
                    print(error_msg)
                    self._save_error_log(chunk_index, "romance", last_json_text, str(e))
        
        # 所有重试都失败，返回空对象
        return PartialRomanceData()
    
    def _fix_json_format(self, json_str: str) -> str:
        """
        修复常见的 JSON 格式错误
        
        Args:
            json_str: 可能有格式错误的 JSON 字符串
            
        Returns:
            修复后的 JSON 字符串
        """
        if not json_str:
            return json_str
        
        import re
        
        # 移除 JSON 注释（// 和 /* */）
        lines = json_str.split('\n')
        cleaned_lines = []
        in_multiline_comment = False
        
        for line in lines:
            # 处理多行注释
            if '/*' in line:
                in_multiline_comment = True
                line = line.split('/*')[0]
            if '*/' in line:
                in_multiline_comment = False
                line = line.split('*/', 1)[1]
                if not line.strip():
                    continue
            if in_multiline_comment:
                continue
            
            # 移除单行注释（但要小心字符串中的 //）
            if '//' in line:
                # 简单处理：只移除行尾注释
                line = re.sub(r'(\s*)//.*$', r'\1', line)
            
            cleaned_lines.append(line)
        
        json_str = '\n'.join(cleaned_lines)
        
        # 修复常见的格式问题
        # 1. 移除末尾多余的逗号（在对象或数组的最后一个元素后）
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        return json_str.strip()
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        从 AI 响应中提取 JSON（可能包含 Markdown 代码块）
        
        Args:
            response: AI 响应文本
            
        Returns:
            清理后的 JSON 字符串
        """
        # 尝试提取 JSON 代码块
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_text = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_text = response[start:end].strip()
        else:
            # 尝试找到 JSON 对象的起始和结束
            start = response.find("{")
            end = response.rfind("}") + 1
            
            if start >= 0 and end > start:
                json_text = response[start:end]
            else:
                json_text = response.strip()
        
        # 修复 JSON 格式
        json_text = self._fix_json_format(json_text)
        
        return json_text
    
    def _parse_json_with_retry(self, json_text: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        尝试解析 JSON，如果失败则尝试修复后重试
        
        Args:
            json_text: JSON 字符串
            max_retries: 最大重试次数
            
        Returns:
            解析后的字典，如果失败返回 None
        """
        for attempt in range(max_retries):
            try:
                # 尝试直接解析
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError as e:
                if attempt == max_retries - 1:
                    # 最后一次尝试，返回 None
                    return None
                
                # 尝试修复 JSON
                json_text = self._fix_json_format(json_text)
        
        return None
    
    def _save_error_log(self, chunk_index: int, chunk_type: str, json_text: str, error_msg: str):
        """
        保存失败的 JSON 片段到错误日志文件，便于调试
        
        Args:
            chunk_index: 块索引
            chunk_type: 块类型（"world" 或 "romance"）
            json_text: 失败的 JSON 文本
            error_msg: 错误信息
        """
        try:
            error_log_dir = Path("output") / "error_logs"
            error_log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_file = error_log_dir / f"{chunk_type}_chunk_{chunk_index}_{timestamp}.txt"
            
            with open(error_file, "w", encoding="utf-8") as f:
                f.write(f"块类型: {chunk_type}\n")
                f.write(f"块索引: {chunk_index}\n")
                f.write(f"错误时间: {timestamp}\n")
                f.write(f"错误信息: {error_msg}\n")
                f.write("=" * 80 + "\n")
                f.write("失败的 JSON 文本:\n")
                f.write("=" * 80 + "\n")
                f.write(json_text[:5000])  # 只保存前5000字符
                if len(json_text) > 5000:
                    f.write(f"\n\n... (已截断，总长度: {len(json_text)} 字符)")
            
            print(f"  💾 错误日志已保存: {error_file}")
        except Exception as e:
            print(f"  ⚠️ 保存错误日志失败: {e}")


# ============================================================
# 3. HeroineSynthesizer - 女主合成器（Reduce Step）
# ============================================================

class HeroineSynthesizer:
    """
    女主合成器 - Reduce 步骤
    将所有收集的素材汇总，生成深度女主设定
    """
    
    def __init__(self, client: AsyncOpenAI, model: str = MODEL_NAME):
        """
        初始化合成器
        
        Args:
            client: OpenAI 异步客户端
            model: 模型名称
        """
        self.client = client
        self.model = model
    
    async def synthesize_heroine_profile(
        self,
        dialogue_snippets: List[str],
        psychology_clues: List[str],
        interaction_events: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        合成女主的心理侧写和说话风格
        
        Args:
            dialogue_snippets: 女主台词原句列表
            psychology_clues: 心理描写片段列表
            interaction_events: 互动事件列表
            
        Returns:
            (psychological_profile, speech_pattern) 元组
        """
        system_prompt = """你是一个专业的角色设定分析师。
你的任务是基于收集的素材，生成深度的人物心理侧写和说话风格分析。

要求：
1. psychological_profile: 深度心理侧写，包含：
   - 核心价值观（重视什么，害怕什么）
   - 情感模式（如何表达情感，如何应对冲突）
   - 过往经历对性格的影响
   - 对恋爱的态度和期待
   - 内心矛盾和成长方向

2. speech_pattern: 说话风格描述，包含：
   - 语气特征（温柔、直接、傲娇等）
   - 惯用词汇或口头禅
   - 句式特点（短句、长句、反问句等）
   - 不同情感状态下的语言变化
   - 提供 Few-Shot 示例

输出格式：
{
  "psychological_profile": "详细的心理侧写...",
  "speech_pattern": "详细的说话风格描述，包含示例..."
}"""

        # 准备素材
        dialogue_text = "\n".join([f"- {d}" for d in dialogue_snippets[:50]])  # 限制数量
        psychology_text = "\n".join([f"- {c}" for c in psychology_clues[:50]])
        
        user_prompt = f"""基于以下收集的素材，生成女主的深度人设：

【女主台词原句】（共 {len(dialogue_snippets)} 条）：
{dialogue_text}

【心理描写片段】（共 {len(psychology_clues)} 条）：
{psychology_text}

【关键互动事件】（共 {len(interaction_events)} 个）：
{json.dumps(interaction_events[:10], ensure_ascii=False, indent=2)}

请综合分析这些素材，生成：
1. psychological_profile: 深度心理侧写（500-800字）
2. speech_pattern: 说话风格描述（300-500字，包含具体示例）

输出 JSON 格式。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=4000,
            )
            
            response_text = response.choices[0].message.content
            
            # 提取 JSON
            json_text = response_text
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_text = response_text[start:end].strip()
            
            data = json.loads(json_text)
            
            psychological_profile = data.get("psychological_profile", "")
            speech_pattern = data.get("speech_pattern", "")
            
            print(f"[Synthesizer] 女主设定合成完成")
            print(f"  心理侧写长度: {len(psychological_profile)} 字符")
            print(f"  说话风格长度: {len(speech_pattern)} 字符")
            
            return psychological_profile, speech_pattern
        
        except Exception as e:
            print(f"[错误] 女主设定合成失败: {e}")
            return "", ""


# ============================================================
# 4. DataAggregator - 数据聚合器（Reduce Step）
# ============================================================

class DataAggregator:
    """
    数据聚合器 - Reduce 步骤
    合并所有 Chunk 的提取结果，生成最终的结构化数据
    """
    
    @staticmethod
    def aggregate_world_lore(partial_lores: List[PartialWorldLore]) -> WorldLore:
        """
        聚合世界观数据
        
        Args:
            partial_lores: 所有 Chunk 的提取结果
            
        Returns:
            完整的 WorldLore 对象
        """
        print(f"\n[Aggregator] 开始聚合世界观数据（{len(partial_lores)} 个块）...")
        
        # 合并规则（去重）
        all_rules = []
        for partial in partial_lores:
            for rule in partial.rules:
                if rule and rule not in all_rules:
                    all_rules.append(rule)
        
        # 合并地点（保留更详细的描述）
        locations = {}
        for partial in partial_lores:
            for name, desc in partial.locations.items():
                if name not in locations or len(desc) > len(locations[name]):
                    locations[name] = desc
        
        # 合并时间线事件（按 timestamp 排序并去重）
        all_events = []
        seen_summaries = set()
        
        for partial in partial_lores:
            for event in partial.timeline_nodes:
                # 去重：基于 summary
                if event.summary not in seen_summaries:
                    all_events.append(event)
                    seen_summaries.add(event.summary)
        
        # 按 timestamp 排序（尝试）
        try:
            all_events.sort(key=lambda e: e.timestamp)
        except:
            pass  # 如果时间戳格式不一致，保持原顺序
        
        # 合并势力（保留更详细的描述）
        factions = {}
        for partial in partial_lores:
            for name, desc in partial.factions.items():
                if name not in factions or len(desc) > len(factions[name]):
                    factions[name] = desc
        
        # 合并世界观摘要（选择最长的）
        lore_summaries = [p.lore_summary for p in partial_lores if p.lore_summary]
        lore_summary = max(lore_summaries, key=len) if lore_summaries else ""
        
        # 合并反派类型（统计频率，选择最常见的）
        villian_types = [p.villian_type for p in partial_lores if p.villian_type]
        if villian_types:
            # 简单统计：选择最长的（通常更详细）
            villian_type = max(villian_types, key=len)
        else:
            villian_type = ""
        
        world_lore = WorldLore(
            rules=all_rules,
            locations=locations,
            timeline_nodes=all_events,
            factions=factions,
            lore_summary=lore_summary,
            villian_type=villian_type  # 关键：保留
        )
        
        print(f"[Aggregator] 世界观聚合完成:")
        print(f"  规则: {len(world_lore.rules)} 条")
        print(f"  地点: {len(world_lore.locations)} 个")
        print(f"  时间线事件: {len(world_lore.timeline_nodes)} 个")
        print(f"  势力: {len(world_lore.factions)} 个")
        print(f"  反派类型: {'已提取' if world_lore.villian_type else '未提取'}")
        
        return world_lore
    
    @staticmethod
    def aggregate_romance_script(
        partial_data_list: List[PartialRomanceData],
        psychological_profile: str,
        speech_pattern: str
    ) -> RomanceScript:
        """
        聚合恋爱剧本数据
        
        Args:
            partial_data_list: 所有 Chunk 的提取结果
            psychological_profile: 合成的心理侧写
            speech_pattern: 合成的说话风格
            
        Returns:
            完整的 RomanceScript 对象
        """
        print(f"\n[Aggregator] 开始聚合恋爱数据（{len(partial_data_list)} 个块）...")
        
        # 合并互动事件（去重）
        all_events = []
        seen_event_names = set()
        
        for partial in partial_data_list:
            for event in partial.interaction_events:
                event_name = event.get("event_name", "")
                if event_name and event_name not in seen_event_names:
                    all_events.append(event)
                    seen_event_names.add(event_name)
        
        # 合并对话范例（去重）
        all_dialogues = []
        for partial in partial_data_list:
            for dialogue in partial.dialogue_snippets:
                if dialogue and dialogue not in all_dialogues:
                    all_dialogues.append(dialogue)
        
        # 合并感情发展阶段（去重）
        all_stages = []
        for partial in partial_data_list:
            for stage in partial.relationship_stages:
                if stage and stage not in all_stages:
                    all_stages.append(stage)
        
        # 合并情感触发器
        all_triggers = {}
        for partial in partial_data_list:
            all_triggers.update(partial.emotional_triggers)
        
        # 合并可能结局（去重）
        all_endings = []
        seen_endings = set()
        for partial in partial_data_list:
            for ending in partial.possible_ending:
                if ending and ending not in seen_endings:
                    all_endings.append(ending)
                    seen_endings.add(ending)
        
        # 合并恋爱线摘要（选择最长的）
        summaries = [p.romance_summary for p in partial_data_list if p.romance_summary]
        romance_summary = max(summaries, key=len) if summaries else ""
        
        romance_script = RomanceScript(
            interaction_events=all_events,
            dialogue_examples=all_dialogues,
            relationship_stages=all_stages,
            emotional_triggers=all_triggers,
            possible_ending=all_endings,  # 关键：保留
            romance_summary=romance_summary
        )
        
        print(f"[Aggregator] 恋爱数据聚合完成:")
        print(f"  互动事件: {len(romance_script.interaction_events)} 个")
        print(f"  对话范例: {len(romance_script.dialogue_examples)} 条")
        print(f"  感情阶段: {len(romance_script.relationship_stages)} 个")
        print(f"  情感触发器: {len(romance_script.emotional_triggers)} 个")
        print(f"  可能结局: {len(romance_script.possible_ending)} 个")
        print(f"  心理侧写: {'已合成' if psychological_profile else '未合成'}")
        print(f"  说话风格: {'已合成' if speech_pattern else '未合成'}")
        
        return romance_script


# ============================================================
# 5. 主流程
# ============================================================

async def extract_world_lore(
    file_path: Path,
    extractor: DeepSeekExtractor
) -> WorldLore:
    """
    提取世界观数据的主流程
    
    Args:
        file_path: 世界观小说文件路径
        extractor: 提取器实例
        
    Returns:
        WorldLore 对象
    """
    print("\n" + "=" * 70)
    print("📖 开始提取世界观数据")
    print("=" * 70)
    
    # 1. 加载和切片
    loader = NovelLoader()
    text = loader.load_file(file_path)
    chunks = loader.split_into_chunks(text)
    
    # 2. Map: 并行提取
    print(f"\n[Map Step] 开始并行提取 {len(chunks)} 个文本块...")
    tasks = [
        extractor.extract_world_chunk(chunk, i)
        for i, chunk in enumerate(chunks)
    ]
    partial_lores = await asyncio.gather(*tasks)
    
    # 3. Reduce: 聚合数据
    print(f"\n[Reduce Step] 开始聚合数据...")
    world_lore = DataAggregator.aggregate_world_lore(partial_lores)
    
    return world_lore


async def extract_romance_script(
    file_path: Path,
    extractor: DeepSeekExtractor,
    synthesizer: HeroineSynthesizer
) -> Tuple[RomanceScript, str, str]:
    """
    提取恋爱剧本数据的主流程
    
    Args:
        file_path: 恋爱小说文件路径
        extractor: 提取器实例
        synthesizer: 女主合成器实例
        
    Returns:
        (RomanceScript, psychological_profile, speech_pattern) 元组
    """
    print("\n" + "=" * 70)
    print("💕 开始提取恋爱数据")
    print("=" * 70)
    
    # 1. 加载和切片
    loader = NovelLoader()
    text = loader.load_file(file_path)
    chunks = loader.split_into_chunks(text)
    
    # 2. Map: 并行提取
    print(f"\n[Map Step] 开始并行提取 {len(chunks)} 个文本块...")
    tasks = [
        extractor.extract_romance_chunk(chunk, i)
        for i, chunk in enumerate(chunks)
    ]
    partial_data_list = await asyncio.gather(*tasks)
    
    # 3. 收集所有素材
    all_dialogues = []
    all_psychology = []
    all_events = []
    
    for partial in partial_data_list:
        all_dialogues.extend(partial.dialogue_snippets)
        all_psychology.extend(partial.psychology_clues)
        all_events.extend(partial.interaction_events)
    
    print(f"\n[Reduce Step - Heroine] 收集到 {len(all_dialogues)} 条台词, {len(all_psychology)} 条心理线索")
    
    # 4. Reduce: 合成女主设定
    psychological_profile, speech_pattern = await synthesizer.synthesize_heroine_profile(
        all_dialogues,
        all_psychology,
        all_events
    )
    
    # 5. Reduce: 聚合恋爱数据
    romance_script = DataAggregator.aggregate_romance_script(
        partial_data_list,
        psychological_profile,
        speech_pattern
    )
    
    return romance_script, psychological_profile, speech_pattern


async def main():
    """主执行函数"""
    print("=" * 70)
    print("🚀 ETL Pipeline - 数据提取管道")
    print("=" * 70)
    print(f"模型: {MODEL_NAME}")
    print(f"并发数: {MAX_CONCURRENT_REQUESTS}")
    print(f"块大小: ~{CHUNK_SIZE_TOKENS} tokens (~{CHUNK_SIZE_CHARS} 字符)")
    print("=" * 70)
    
    # 检查并获取 API Key
    try:
        api_key = get_api_key()
    except ValueError as e:
        print(f"[错误] {e}")
        return
    
    # 初始化组件
    extractor = DeepSeekExtractor(api_key)
    synthesizer = HeroineSynthesizer(extractor.client)
    
    # 文件路径
    data_dir = Path("data")
    world_file = data_dir / "world_novel_cleaned.txt"
    romance_file = data_dir / "romance_novel_cleaned.txt"
    
    # 检查文件是否存在
    if not world_file.exists():
        print(f"[警告] 世界观小说文件不存在: {world_file}")
        print("      请确保文件已准备好")
    
    if not romance_file.exists():
        print(f"[警告] 恋爱小说文件不存在: {romance_file}")
        print("      请确保文件已准备好")
    
    # 创建输出目录
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # 提取世界观数据
    if world_file.exists():
        try:
            world_lore = await extract_world_lore(world_file, extractor)
            
            # 保存结果
            output_file = output_dir / "world_lore.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    world_lore.model_dump(mode="json"),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
            print(f"\n✅ 世界观数据已保存: {output_file}")
            results["world_lore"] = world_lore
        
        except Exception as e:
            print(f"\n❌ 世界观数据提取失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⏭️  跳过世界观提取（文件不存在）")
    
    # 提取恋爱数据
    if romance_file.exists():
        try:
            romance_script, psychological_profile, speech_pattern = await extract_romance_script(
                romance_file,
                extractor,
                synthesizer
            )
            
            # 保存结果
            output_file = output_dir / "romance_script.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(
                    romance_script.model_dump(mode="json"),
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            
            # 保存女主设定（单独的 JSON）
            if psychological_profile or speech_pattern:
                heroine_data = {
                    "psychological_profile": psychological_profile,
                    "speech_pattern": speech_pattern
                }
                heroine_file = output_dir / "heroine_profile.json"
                with open(heroine_file, "w", encoding="utf-8") as f:
                    json.dump(heroine_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 女主设定已保存: {heroine_file}")
            
            print(f"\n✅ 恋爱数据已保存: {output_file}")
            results["romance_script"] = romance_script
            results["heroine_profile"] = {
                "psychological_profile": psychological_profile,
                "speech_pattern": speech_pattern
            }
        
        except Exception as e:
            print(f"\n❌ 恋爱数据提取失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⏭️  跳过恋爱数据提取（文件不存在）")
    
    # 总结
    print("\n" + "=" * 70)
    print("🎉 ETL Pipeline 执行完成！")
    print("=" * 70)
    
    if results:
        print("\n📊 提取结果摘要:")
        if "world_lore" in results:
            wl = results["world_lore"]
            print(f"  世界观:")
            print(f"    - 规则: {len(wl.rules)} 条")
            print(f"    - 地点: {len(wl.locations)} 个")
            print(f"    - 时间线事件: {len(wl.timeline_nodes)} 个")
            print(f"    - 势力: {len(wl.factions)} 个")
            print(f"    - 反派类型: {'✓' if wl.villian_type else '✗'}")
        
        if "romance_script" in results:
            rs = results["romance_script"]
            print(f"  恋爱线:")
            print(f"    - 互动事件: {len(rs.interaction_events)} 个")
            print(f"    - 对话范例: {len(rs.dialogue_examples)} 条")
            print(f"    - 可能结局: {len(rs.possible_ending)} 个")
        
        if "heroine_profile" in results:
            hp = results["heroine_profile"]
            print(f"  女主设定:")
            print(f"    - 心理侧写: {'✓' if hp['psychological_profile'] else '✗'}")
            print(f"    - 说话风格: {'✓' if hp['speech_pattern'] else '✗'}")
    else:
        print("  未提取到任何数据（请检查输入文件）")


if __name__ == "__main__":
    asyncio.run(main())

