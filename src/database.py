"""
数据库初始化与操作
包含 SQLite (用于存档) 和 LanceDB (用于 Style-RAG) 的初始化和操作函数
"""
import sqlite3
import json
import lancedb
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from .models import GameState, SaveSlot


# 数据库文件路径
DB_DIR = Path("data")
SQLITE_DB_PATH = DB_DIR / "saves.db"
LANCEDB_PATH = DB_DIR / "lancedb"

# 确保数据目录存在
DB_DIR.mkdir(exist_ok=True)


class SQLiteDatabase:
    """SQLite 数据库管理类 - 用于游戏存档"""
    
    def __init__(self, db_path: Path = SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库和表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建存档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS save_slots (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                json_data TEXT NOT NULL,
                preview_text TEXT DEFAULT ''
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_game(self, slot_id: int, game_state: GameState) -> bool:
        """
        保存游戏状态到指定槽位
        
        Args:
            slot_id: 存档槽位ID
            game_state: 游戏状态对象
            
        Returns:
            bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 序列化游戏状态
            json_data = game_state.model_dump_json()
            timestamp = datetime.now().isoformat()
            
            # 生成预览文本
            preview_text = (
                f"回合 {game_state.turn_count} - "
                f"{game_state.current_location} - "
                f"玩家: {game_state.player_name}"
            )
            
            # 使用 REPLACE 来插入或更新
            cursor.execute("""
                REPLACE INTO save_slots (id, timestamp, json_data, preview_text)
                VALUES (?, ?, ?, ?)
            """, (slot_id, timestamp, json_data, preview_text))
            
            conn.commit()
            conn.close()
            
            print(f"[数据库] 成功保存游戏到槽位 {slot_id}")
            return True
            
        except Exception as e:
            print(f"[数据库] 保存游戏失败: {e}")
            return False
    
    def load_game(self, slot_id: int) -> Optional[GameState]:
        """
        从指定槽位加载游戏状态
        
        Args:
            slot_id: 存档槽位ID
            
        Returns:
            Optional[GameState]: 游戏状态对象，如果不存在则返回 None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT json_data FROM save_slots WHERE id = ?
            """, (slot_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                json_data = result[0]
                game_state = GameState.model_validate_json(json_data)
                print(f"[数据库] 成功从槽位 {slot_id} 加载游戏")
                return game_state
            else:
                print(f"[数据库] 槽位 {slot_id} 不存在")
                return None
                
        except Exception as e:
            print(f"[数据库] 加载游戏失败: {e}")
            return None
    
    def get_all_saves(self) -> List[dict]:
        """
        获取所有存档信息（不包含完整游戏数据）
        
        Returns:
            List[dict]: 存档信息列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, timestamp, preview_text FROM save_slots
                ORDER BY timestamp DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            saves = []
            for row in results:
                saves.append({
                    "slot_id": row[0],
                    "timestamp": row[1],
                    "preview_text": row[2]
                })
            
            return saves
            
        except Exception as e:
            print(f"[数据库] 获取存档列表失败: {e}")
            return []
    
    def delete_save(self, slot_id: int) -> bool:
        """
        删除指定槽位的存档
        
        Args:
            slot_id: 存档槽位ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM save_slots WHERE id = ?", (slot_id,))
            
            conn.commit()
            conn.close()
            
            print(f"[数据库] 成功删除槽位 {slot_id} 的存档")
            return True
            
        except Exception as e:
            print(f"[数据库] 删除存档失败: {e}")
            return False


class LanceDBDatabase:
    """LanceDB 数据库管理类 - 用于 Style-RAG"""
    
    def __init__(self, db_path: Path = LANCEDB_PATH):
        self.db_path = db_path
        self.db = None
        self._init_database()
    
    def _init_database(self):
        """初始化 LanceDB 连接"""
        try:
            # 连接到 LanceDB
            self.db = lancedb.connect(str(self.db_path))
            
            # 检查是否存在 novel_chunks 表，如果不存在则创建占位表
            table_names = self.db.table_names()
            
            if "novel_chunks" not in table_names:
                # 创建占位表（暂不实现具体逻辑）
                # 定义表结构：文本内容、向量嵌入、元数据
                print("[LanceDB] 初始化 novel_chunks 表（占位）")
                # 注意: 实际使用时需要提供真实的向量数据
                # 这里只是创建表结构的占位符
            else:
                print("[LanceDB] novel_chunks 表已存在")
            
            print(f"[LanceDB] 成功连接到数据库: {self.db_path}")
            
        except Exception as e:
            print(f"[LanceDB] 初始化失败: {e}")
            self.db = None
    
    def add_chunk(self, text: str, metadata: dict = None) -> bool:
        """
        添加文本片段到数据库（占位函数）
        
        Args:
            text: 文本内容
            metadata: 元数据字典
            
        Returns:
            bool: 是否成功
        """
        # TODO: 实现向量化和存储逻辑
        print(f"[LanceDB] 添加文本片段（占位功能）: {text[:50]}...")
        return True
    
    def search_similar(self, query: str, limit: int = 5) -> List[dict]:
        """
        搜索相似文本片段（占位函数）
        
        Args:
            query: 查询文本
            limit: 返回结果数量
            
        Returns:
            List[dict]: 相似文本列表
        """
        # TODO: 实现向量相似度搜索逻辑
        print(f"[LanceDB] 搜索相似文本（占位功能）: {query[:50]}...")
        return []


# 创建全局数据库实例
sqlite_db = SQLiteDatabase()
lancedb_db = LanceDBDatabase()


# 便捷函数
def save_game(slot_id: int, game_state: GameState) -> bool:
    """保存游戏到指定槽位"""
    return sqlite_db.save_game(slot_id, game_state)


def load_game(slot_id: int) -> Optional[GameState]:
    """从指定槽位加载游戏"""
    return sqlite_db.load_game(slot_id)


def get_all_saves() -> List[dict]:
    """获取所有存档信息"""
    return sqlite_db.get_all_saves()


def delete_save(slot_id: int) -> bool:
    """删除指定槽位的存档"""
    return sqlite_db.delete_save(slot_id)




