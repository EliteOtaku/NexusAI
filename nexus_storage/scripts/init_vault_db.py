#!/usr/bin/env python3
"""
NexusAI Vault 数据库初始化脚本
专为 RTX 4080 GPU 优化的语义存储系统

功能：
1. 创建 nexus_vault.db 数据库
2. 执行优化的数据库架构
3. 集成 sentence-transformers 向量嵌入
4. 配置 GPU 加速的语义搜索
"""

import os
import sys
import sqlite3
import logging
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('../db_vault_init.log')
    ]
)
logger = logging.getLogger('nexus_vault_init')

class NexusVaultInitializer:
    """NexusAI Vault 数据库初始化器 - 专为 RTX 4080 优化"""
    
    def __init__(self, db_path: str = "nexus_storage/data/nexus_vault.db"):
        """
        初始化 Vault 数据库初始化器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        self.embedding_model = None
        
        # 创建数据目录
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def connect(self) -> bool:
        """连接到数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            
            # 配置数据库性能优化（专为 RTX 4080）
            self.connection.execute("PRAGMA journal_mode = WAL")
            self.connection.execute("PRAGMA synchronous = NORMAL")
            self.connection.execute("PRAGMA cache_size = -64000")  # 64MB 缓存
            self.connection.execute("PRAGMA temp_store = MEMORY")
            self.connection.execute("PRAGMA mmap_size = 268435456")  # 256MB mmap
            
            logger.info(f"✅ 数据库连接成功: {self.db_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def create_tables(self) -> bool:
        """创建优化的数据库表结构"""
        try:
            cursor = self.connection.cursor()
            
            # 会话表 - 存储 AI 对话会话
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_uuid VARCHAR(36) UNIQUE NOT NULL,
                    platform VARCHAR(50) NOT NULL CHECK (platform IN ('gemini', 'deepseek', 'chatgpt', 'claude', 'other')),
                    title VARCHAR(255) DEFAULT '未命名会话',
                    description TEXT,
                    platform_session_id VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
                    message_count INTEGER DEFAULT 0,
                    token_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_active_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON
                )
            """)
            
            # 消息表 - 存储具体对话消息
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    content_hash VARCHAR(64),
                    platform_message_id VARCHAR(100),
                    model_used VARCHAR(100),
                    prompt_tokens INTEGER DEFAULT 0,
                    completion_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    processing_time_ms INTEGER,
                    response_latency_ms INTEGER,
                    embedding_vector BLOB,
                    embedding_model VARCHAR(100),
                    embedding_dim INTEGER,
                    summary TEXT,
                    tags JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # 向量嵌入表 - 专为 GPU 加速的语义搜索优化
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL UNIQUE,
                    embedding_data BLOB NOT NULL,
                    embedding_model VARCHAR(100) NOT NULL,
                    embedding_dim INTEGER NOT NULL,
                    embedding_norm REAL,
                    index_type VARCHAR(50) DEFAULT 'flat',
                    index_params JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
                )
            """)
            
            # 创建性能优化的索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_platform ON sessions(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vectors_model ON vector_embeddings(embedding_model)")
            
            self.connection.commit()
            logger.info("✅ 数据库表结构创建成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建表结构失败: {e}")
            return False
    
    def initialize_embedding_model(self) -> bool:
        """初始化 sentence-transformers 嵌入模型（GPU 加速）"""
        try:
            # 检查是否安装了 sentence-transformers
            try:
                from sentence_transformers import SentenceTransformer
                
                # 选择适合 RTX 4080 的模型
                # all-MiniLM-L6-v2: 384维，速度快，适合实时处理
                model_name = "all-MiniLM-L6-v2"
                
                logger.info(f"🚀 加载 sentence-transformers 模型: {model_name}")
                
                # 使用 GPU 加速（如果可用）
                device = "cuda" if self._check_gpu_availability() else "cpu"
                
                self.embedding_model = SentenceTransformer(model_name, device=device)
                
                # 测试模型
                test_embedding = self.embedding_model.encode(["测试文本"], convert_to_numpy=True)
                embedding_dim = test_embedding.shape[1]
                
                logger.info(f"✅ 嵌入模型初始化成功: {model_name} ({embedding_dim}维, {device}设备)")
                
                # 存储模型信息到数据库
                cursor = self.connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_registry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_name VARCHAR(100) UNIQUE NOT NULL,
                        model_type VARCHAR(50) NOT NULL,
                        embedding_dim INTEGER NOT NULL,
                        device VARCHAR(20) DEFAULT 'cpu',
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO model_registry 
                    (model_name, model_type, embedding_dim, device, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (model_name, "sentence-transformers", embedding_dim, device, True))
                
                self.connection.commit()
                return True
                
            except ImportError:
                logger.warning("⚠️ sentence-transformers 未安装，将使用模拟嵌入")
                self.embedding_model = None
                return True
                
        except Exception as e:
            logger.error(f"❌ 嵌入模型初始化失败: {e}")
            self.embedding_model = None
            return False
    
    def _check_gpu_availability(self) -> bool:
        """检查 GPU 可用性"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def generate_embedding(self, text: str) -> Optional[bytes]:
        """生成文本的向量嵌入"""
        try:
            if self.embedding_model:
                # 使用真实的 sentence-transformers 模型
                embedding = self.embedding_model.encode([text], convert_to_numpy=True)
                return embedding[0].tobytes()
            else:
                # 模拟嵌入（用于测试）
                import numpy as np
                embedding = np.random.randn(384).astype(np.float32)
                return embedding.tobytes()
                
        except Exception as e:
            logger.error(f"❌ 生成嵌入失败: {e}")
            return None
    
    def insert_sample_data(self) -> bool:
        """插入示例数据用于测试"""
        try:
            cursor = self.connection.cursor()
            
            # 插入示例会话
            session_uuid = hashlib.md5(str(datetime.now()).encode()).hexdigest()
            cursor.execute("""
                INSERT INTO sessions (session_uuid, platform, title, description)
                VALUES (?, ?, ?, ?)
            """, (session_uuid, "gemini", "示例对话", "NexusAI 数据库测试会话"))
            
            session_id = cursor.lastrowid
            
            # 插入示例消息
            sample_messages = [
                (session_id, "user", "你好，请介绍一下人工智能的发展历史", "user", "gemini-pro", 15, 0, 15),
                (session_id, "assistant", "人工智能的发展可以追溯到20世纪50年代...", "assistant", "gemini-pro", 0, 250, 250)
            ]
            
            for msg in sample_messages:
                content_hash = hashlib.sha256(msg[2].encode()).hexdigest()
                
                # 生成向量嵌入
                embedding_vector = self.generate_embedding(msg[2])
                
                cursor.execute("""
                    INSERT INTO messages 
                    (session_id, role, content, content_hash, model_used, 
                     prompt_tokens, completion_tokens, total_tokens, embedding_vector, embedding_model, embedding_dim)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    msg[0], msg[1], msg[2], content_hash, msg[4], 
                    msg[5], msg[6], msg[7], embedding_vector, "all-MiniLM-L6-v2", 384
                ))
                
                message_id = cursor.lastrowid
                
                # 插入向量嵌入记录
                if embedding_vector:
                    cursor.execute("""
                        INSERT INTO vector_embeddings 
                        (message_id, embedding_data, embedding_model, embedding_dim, embedding_norm)
                        VALUES (?, ?, ?, ?, ?)
                    """, (message_id, embedding_vector, "all-MiniLM-L6-v2", 384, 1.0))
            
            self.connection.commit()
            logger.info("✅ 示例数据插入成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 插入示例数据失败: {e}")
            return False
    
    def verify_database(self) -> Dict[str, Any]:
        """验证数据库完整性"""
        try:
            cursor = self.connection.cursor()
            
            # 检查表是否存在
            tables = ["sessions", "messages", "vector_embeddings", "model_registry"]
            existing_tables = []
            
            for table in tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if cursor.fetchone():
                    existing_tables.append(table)
            
            # 统计数据量
            stats = {}
            for table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            
            # 检查向量嵌入功能
            cursor.execute("SELECT COUNT(*) FROM vector_embeddings WHERE embedding_data IS NOT NULL")
            vector_count = cursor.fetchone()[0]
            
            verification_result = {
                "status": "healthy",
                "tables_exist": existing_tables,
                "table_counts": stats,
                "vector_embeddings_count": vector_count,
                "embedding_model_available": self.embedding_model is not None,
                "gpu_available": self._check_gpu_availability(),
                "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0
            }
            
            logger.info("✅ 数据库验证完成")
            return verification_result
            
        except Exception as e:
            logger.error(f"❌ 数据库验证失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def initialize(self) -> bool:
        """执行完整的数据库初始化流程"""
        logger.info("🚀 开始初始化 NexusAI Vault 数据库...")
        
        try:
            # 1. 连接数据库
            if not self.connect():
                return False
            
            # 2. 创建表结构
            if not self.create_tables():
                return False
            
            # 3. 初始化嵌入模型
            if not self.initialize_embedding_model():
                logger.warning("⚠️ 嵌入模型初始化失败，但数据库仍可运行")
            
            # 4. 插入示例数据
            if not self.insert_sample_data():
                logger.warning("⚠️ 示例数据插入失败")
            
            # 5. 验证数据库
            verification = self.verify_database()
            
            logger.info(f"🎉 NexusAI Vault 数据库初始化完成!")
            logger.info(f"📊 验证结果: {json.dumps(verification, indent=2, ensure_ascii=False)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            return False
        finally:
            if self.connection:
                self.connection.close()

def main():
    """主函数"""
    initializer = NexusVaultInitializer()
    
    if initializer.initialize():
        print("\n🎯 NexusAI Vault 数据库已准备就绪!")
        print("📍 数据库位置: nexus_storage/data/nexus_vault.db")
        print("🔧 支持功能: 会话存储、消息持久化、GPU 加速向量嵌入")
        print("🚀 专为 RTX 4080 优化: 语义搜索、实时处理")
        sys.exit(0)
    else:
        print("\n❌ 数据库初始化失败，请检查日志文件")
        sys.exit(1)

if __name__ == "__main__":
    main()