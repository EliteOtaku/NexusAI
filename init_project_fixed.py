#!/usr/bin/env python3
"""
NexusAI 项目初始化脚本

此脚本将创建 FastAPI + SQLite + ChromaDB 架构的文件夹结构。
运行此脚本前请确保已安装 Python 3.8+。
"""

import os
import sys
from pathlib import Path

def create_directory(path: Path, description: str = "") -> None:
    """创建目录，如果已存在则跳过"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建目录: {path.relative_to(Path.cwd())} {description}")
    except Exception as e:
        print(f"✗ 创建目录失败 {path}: {e}")

def write_file(path: Path, content: str, description: str = "") -> None:
    """写入文件，如果已存在则跳过"""
    try:
        if path.exists():
            print(f"⚠️ 文件已存在，跳过: {path.relative_to(Path.cwd())}")
            return
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 创建文件: {path.relative_to(Path.cwd())} {description}")
    except Exception as e:
        print(f"✗ 写入文件失败 {path}: {e}")

def create_backend_structure(base_path: Path) -> None:
    """创建后端项目结构"""
    
    # 创建主目录结构
    directories = [
        (base_path / "backend", "后端根目录"),
        (base_path / "backend" / "app", "FastAPI 应用主目录"),
        (base_path / "backend" / "app" / "core", "核心配置和数据库"),
        (base_path / "backend" / "app" / "models", "SQLAlchemy 数据模型"),
        (base_path / "backend" / "app" / "schemas", "Pydantic 模式定义"),
        (base_path / "backend" / "app" / "crud", "数据库 CRUD 操作"),
        (base_path / "backend" / "app" / "api" / "v1" / "endpoints", "API 端点"),
        (base_path / "backend" / "app" / "api" / "v1", "API v1 版本"),
        (base_path / "backend" / "app" / "api", "API 路由"),
        (base_path / "backend" / "app" / "services", "业务逻辑服务"),
        (base_path / "backend" / "app" / "utils", "工具函数"),
        (base_path / "backend" / "data", "数据存储目录 (SQLite, ChromaDB)"),
        (base_path / "backend" / "tests", "测试目录"),
    ]
    
    for directory, desc in directories:
        create_directory(directory, desc)
    
    # 创建 __init__.py 文件
    init_files = [
        base_path / "backend" / "app" / "__init__.py",
        base_path / "backend" / "app" / "core" / "__init__.py",
        base_path / "backend" / "app" / "models" / "__init__.py",
        base_path / "backend" / "app" / "schemas" / "__init__.py",
        base_path / "backend" / "app" / "crud" / "__init__.py",
        base_path / "backend" / "app" / "api" / "__init__.py",
        base_path / "backend" / "app" / "api" / "v1" / "__init__.py",
        base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "__init__.py",
        base_path / "backend" / "app" / "services" / "__init__.py",
        base_path / "backend" / "app" / "utils" / "__init__.py",
        base_path / "backend" / "tests" / "__init__.py",
    ]
    
    for init_file in init_files:
        write_file(init_file, '"""模块初始化文件"""\n', "模块初始化文件")
    
    # 创建配置文件
    create_config_files(base_path)
    
    # 创建数据库模型和模式
    create_database_files(base_path)
    
    # 创建API端点文件
    create_api_files(base_path)
    
    # 创建服务文件
    create_service_files(base_path)
    
    # 创建工具文件
    create_utility_files(base_path)
    
    # 创建测试文件
    create_test_files(base_path)
    
    # 创建根级文件
    create_root_files(base_path)

def create_config_files(base_path: Path) -> None:
    """创建配置文件"""
    
    # config.py
    config_content = """"""
配置管理模块

从环境变量加载配置，支持开发和生产环境。
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    \"\"\"应用配置\"\"\"
    
    # 应用配置
    APP_NAME: str = "NexusAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/nexusai.db"
    
    # ChromaDB 配置
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "conversations"
    
    # Embedding 模型配置
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # 本地运行的轻量级模型
    
    # Ollama 配置 (预留)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    
    # 插件通信配置 (预留)
    PLUGIN_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
"""
    
    # database.py
    database_content = """"""
数据库连接和会话管理

提供 SQLAlchemy 会话工厂和数据库初始化。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db():
    \"\"\"获取数据库会话（依赖注入）\"\"\"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    \"\"\"初始化数据库，创建所有表\"\"\"
    from app.models import conversation  # 导入所有模型以注册它们
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表已创建")
"""
    
    write_file(base_path / "backend" / "app" / "core" / "config.py", config_content, "应用配置管理")
    write_file(base_path / "backend" / "app" / "core" / "database.py", database_content, "数据库连接管理")

def create_database_files(base_path: Path) -> None:
    """创建数据库相关文件"""
    
    # models/conversation.py
    model_content = """"""
对话数据模型

存储用户与AI的对话记录。
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Conversation(Base):
    \"\"\"对话记录模型\"\"\"
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, comment="来源: gemini, deepseek, chatgpt")
    user_message = Column(Text, nullable=False, comment="用户消息")
    ai_response = Column(Text, nullable=False, comment="AI回复")
    metadata = Column(JSON, nullable=True, comment="附加元数据")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    def __repr__(self):
        return f"<Conversation {self.id} from {self.source}>"
"""
    
    # schemas/conversation.py
    schema_content = """"""
对话模式定义

用于API请求和响应的数据验证。
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel

class ConversationBase(BaseModel):
    \"\"\"对话基础模式\"\"\"
    source: str
    user_message: str
    ai_response: str
    metadata: Optional[Any] = None

class ConversationCreate(ConversationBase):
    \"\"\"创建对话的请求模式\"\"\"
    pass

class ConversationUpdate(BaseModel):
    \"\"\"更新对话的请求模式\"\"\"
    user_message: Optional[str] = None
    ai_response: Optional[str] = None
    metadata: Optional[Any] = None

class ConversationInDB(ConversationBase):
    \"\"\"数据库中的对话模式\"\"\"
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationSearchRequest(BaseModel):
    \"\"\"对话搜索请求模式\"\"\"
    query: str
    limit: int = 10
    
class ConversationSearchResult(BaseModel):
    \"\"\"对话搜索结果模式\"\"\"
    id: int
    source: str
    user_message: str
    ai_response: str
    similarity: float
"""
    
    # crud/conversation.py
    crud_content = """"""
对话数据CRUD操作

提供对话记录的创建、读取、更新、删除功能。
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

def get_conversation(db: Session, conversation_id: int):
    \"\"\"根据ID获取对话\"\"\"
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    \"\"\"获取对话列表\"\"\"
    return db.query(Conversation).offset(skip).limit(limit).all()

def create_conversation(db: Session, conversation: ConversationCreate):
    \"\"\"创建新对话记录\"\"\"
    db_conversation = Conversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def update_conversation(db: Session, conversation_id: int, conversation: ConversationUpdate):
    \"\"\"更新对话记录\"\"\"
    db_conversation = get_conversation(db, conversation_id)
    if not db_conversation:
        return None
    
    update_data = conversation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_conversation, field, value)
    
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def delete_conversation(db: Session, conversation_id: int):
    \"\"\"删除对话记录\"\"\"
    db_conversation = get_conversation(db, conversation_id)
    if not db_conversation:
        return None
    
    db.delete(db_conversation)
    db.commit()
    return db_conversation

def search_conversations_text(db: Session, query: str, limit: int = 10):
    \"\"\"文本搜索对话（基于SQL LIKE）\"\"\"
    return db.query(Conversation).filter(
        or_(
            Conversation.user_message.contains(query),
            Conversation.ai_response.contains(query)
        )
    ).limit(limit).all()
"""
    
    write_file(base_path / "backend" / "app" / "models" / "conversation.py", model_content, "对话数据模型")
    write_file(base_path / "backend" / "app" / "schemas" / "conversation.py", schema_content, "对话模式定义")
    write_file(base_path / "backend" / "app" / "crud" / "conversation.py", crud_content, "对话CRUD操作")

def create_api_files(base_path: Path) -> None:
    """创建API端点文件"""
    
    # conversations.py
    conversations_api_content = """"""
对话API端点

提供对话的存储、检索和搜索功能。
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.conversation import (
    ConversationCreate, ConversationInDB, ConversationUpdate,
    ConversationSearchRequest, ConversationSearchResult
)
from app.crud.conversation import (
    create_conversation, get_conversation, get_conversations,
    update_conversation, delete_conversation, search_conversations_text
)
from app.services.vector_store import search_similar_conversations

router = APIRouter()

@router.post("/", response_model=ConversationInDB, status_code=status.HTTP_201_CREATED)
def create_conversation_endpoint(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    \"\"\"创建新的对话记录\"\"\"
    try:
        return create_conversation(db, conversation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建对话失败: {str(e)}"
        )

@router.get("/", response_model=List[ConversationInDB])
def read_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    \"\"\"获取对话列表\"\"\"
    return get_conversations(db, skip=skip, limit=limit)

@router.get("/{conversation_id}", response_model=ConversationInDB)
def read_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    \"\"\"根据ID获取对话\"\"\"
    conversation = get_conversation(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"对话 {conversation_id} 不存在"
        )
    return conversation

@router.put("/{conversation_id}", response_model=ConversationInDB)
def update_conversation_endpoint(
    conversation_id: int,
    conversation: ConversationUpdate,
    db: Session = Depends(get_db)
):
    \"\"\"更新对话记录\"\"\"
    db_conversation = update_conversation(db, conversation_id, conversation)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"对话 {conversation_id} 不存在"
        )
    return db_conversation

@router.delete("/{conversation_id}")
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    \"\"\"删除对话记录\"\"\"
    db_conversation = delete_conversation(db, conversation_id)
    if not db_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"对话 {conversation_id} 不存在"
        )
    return {"message": f"对话 {conversation_id} 已删除"}

@router.post("/search/text", response_model=List[ConversationInDB])
def search_conversations_text_endpoint(
    request: ConversationSearchRequest,
    db: Session = Depends(get_db)
):
    \"\"\"文本搜索对话\"\"\"
    return search_conversations_text(db, request.query, request.limit)

@router.post("/search/semantic", response_model=List[ConversationSearchResult])
def search_conversations_semantic_endpoint(
    request: ConversationSearchRequest,
    db: Session = Depends(get_db)
):
    \"\"\"语义搜索对话（基于向量相似度）\"\"\"
    # 这里调用向量存储服务进行语义搜索
    results = search_similar_conversations(request.query, limit=request.limit)
    return results
"""
    
    # health.py
    health_api_content = """"""
健康检查API端点

用于监控服务状态和依赖项健康。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    \"\"\"基础健康检查\"\"\"
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/database")
async def database_health_check(db: Session = Depends(get_db)):
    \"\"\"数据库健康检查\"\"\"
    try:
        db.execute(text("SELECT 1"))
        return {"database": "healthy"}
    except Exception as e:
        return {"database": "unhealthy", "error": str(e)}

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    \"\"\"详细健康检查报告\"\"\"
    checks = {
        "service": {"status": "healthy", "details": {"name": settings.APP_NAME}},
        "database": {"status": "unknown"},
    }
    
    # 检查数据库
    try:
        db.execute(text("SELECT 1"))
        checks["database"]["status"] = "healthy"
    except Exception as e:
        checks["database"]["status"] = "unhealthy"
        checks["database"]["error"] = str(e)
    
    all_healthy = all(check["status"] == "healthy" for check in checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks
    }
"""
    
    # plugin.py (预留)
    plugin_api_content = """"""
浏览器插件API端点 (预留)

用于与浏览器插件通信，接收实时对话数据。
"""
from fastapi import APIRouter, HTTPException, status, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings

router = APIRouter()
api_key_header = APIKeyHeader(name="X-Plugin-API-Key", auto_error=False)

async def verify_plugin_api_key(api_key: str = Security(api_key_header)):
    \"\"\"验证插件API密钥\"\"\"
    if not api_key or api_key != settings.PLUGIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的插件API密钥"
        )
    return api_key

@router.post("/conversation")
async def receive_conversation_from_plugin(
    conversation_data: dict,
    api_key: str = Security(verify_plugin_api_key)
):
    \"\"\"
    接收来自浏览器插件的对话数据
    
    此接口用于浏览器插件实时推送对话记录到后端。
    \"\"\"
    # TODO: 实现对话数据验证和存储逻辑
    return {
        "status": "received",
        "message": "对话数据已接收（预留接口）",
        "data": conversation_data
    }

@router.get("/status")
async def plugin_status():
    \"\"\"获取插件连接状态\"\"\"
    return {
        "status": "ready",
        "message": "插件API已就绪（预留接口）"
    }
"""
    
    # ollama.py (预留)
    ollama_api_content = """"""
Ollama集成API端点 (预留)

用于与本地Ollama服务通信，实现对话摘要生成。
"""
from fastapi import APIRouter, HTTPException, status
import httpx
from typing import Optional

from app.core.config import settings

router = APIRouter()

@router.post("/summarize")
async def summarize_conversation(
    conversation_text: str,
    model: Optional[str] = None
):
    \"\"\"
    使用Ollama生成对话摘要
    
    此接口将调用本地Ollama服务对对话进行摘要生成。
    \"\"\"
    target_model = model or settings.OLLAMA_MODEL
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": target_model,
                    "prompt": f"请将以下对话内容浓缩成一段简明的摘要，保留核心逻辑和关键信息：\n\n{conversation_text}",
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "summary": result.get("response", ""),
                    "model": target_model,
                    "processing_time": result.get("total_duration", 0) / 1_000_000_000  # 转换为秒
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Ollama服务错误: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"无法连接到Ollama服务: {str(e)}"
        )

@router.get("/models")
async def list_available_models():
    \"\"\"获取可用的Ollama模型列表\"\"\"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"获取模型列表失败: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"无法连接到Ollama服务: {str(e)}"
        )
"""
    
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "conversations.py", conversations_api_content, "对话API端点")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "health.py", health_api_content, "健康检查API")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "plugin.py", plugin_api_content, "浏览器插件API（预留）")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "ollama.py", ollama_api_content, "Ollama集成API（预留）")

def create_service_files(base_path: Path) -> None:
    """创建服务文件"""
    
    # embedding_service.py
    embedding_service_content = """"""
Embedding服务

使用本地模型生成文本向量嵌入，支持ChromaDB向量存储。
"""
import numpy as np
from typing import List, Optional
import logging

# 尝试导入sentence-transformers，如果未安装则使用回退方案
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers 未安装，将使用简易嵌入生成器")

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    \"\"\"文本嵌入服务\"\"\"
    
    def __init__(self):
        self.model = None
        self.model_name = settings.EMBEDDING_MODEL
        self._initialize_model()
    
    def _initialize_model(self):
        \"\"\"初始化嵌入模型\"\"\"
        try:
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                logger.info(f"加载嵌入模型: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("嵌入模型加载成功")
            else:
                logger.warning("使用简易嵌入生成器（仅用于测试）")
                self.model = None
        except Exception as e:
            logger.error(f"加载嵌入模型失败: {e}")
            self.model = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        \"\"\"获取文本的向量嵌入\"\"\"
        if not text or not text.strip():
            return None
        
        try:
            if self.model:
                # 使用sentence-transformers
                embedding = self.model.encode(text)
                return embedding.tolist()
            else:
                # 简易回退：使用词频向量（仅用于测试）
                return self._simple_embedding(text)
        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            return None
    
    def get_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        \"\"\"批量获取文本向量嵌入\"\"\"
        if not texts:
            return None
        
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            if embedding:
                embeddings.append(embedding)
        
        return embeddings if embeddings else None
    
    def _simple_embedding(self, text: str) -> List[float]:
        \"\"\"简易嵌入生成器（仅用于测试）\"\"\"
        # 这是一个简化的示例实现
        # 实际项目中应该使用真正的嵌入模型
        import hashlib
        import struct
        
        # 使用哈希生成固定长度的伪向量
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # 将哈希转换为16个浮点数
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            if i + 4 <= len(hash_bytes):
                value = struct.unpack('f', hash_bytes[i:i+4])[0]
                embedding.append(value)
        
        # 填充到384维（与all-MiniLM-L6-v2相同）
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]

# 全局嵌入服务实例
embedding_service = EmbeddingService()
"""
    
    # vector_store.py
    vector_store_content = """"""
向量存储服务

管理ChromaDB向量数据库，提供对话的向量化存储和语义搜索。
"""
import logging
from typing import List, Optional, Tuple
import uuid
from datetime import datetime

# 尝试导入ChromaDB
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logging.warning("chromadb 未安装，向量存储功能不可用")

from app.core.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class VectorStoreService:
    \"\"\"向量存储服务\"\"\"
    
    def __init__(self):
        self.client = None
        self.collection = None
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        \"\"\"初始化ChromaDB连接\"\"\"
        if not CHROMA_AVAILABLE:
            logger.warning("ChromaDB不可用，向量存储服务将无法工作")
            return
        
        try:
            # 创建ChromaDB客户端
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIRECTORY,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "NexusAI对话向量存储"}
            )
            
            logger.info(f"ChromaDB初始化成功，集合: {settings.CHROMA_COLLECTION_NAME}")
            logger.info(f"向量存储位置: {settings.CHROMA_PERSIST_DIRECTORY}")
            
        except Exception as e:
            logger.error(f"初始化ChromaDB失败: {e}")
            self.client = None
            self.collection = None
    
    def is_available(self) -> bool:
        \"\"\"检查向量存储是否可用\"\"\"
        return CHROMA_AVAILABLE and self.collection is not None
    
    def add_conversation(
        self,
        conversation_id: int,
        source: str,
        user_message: str,
        ai_response: str,
        metadata: Optional[dict] = None
    ) -> bool:
        \"\"\"
        添加对话到向量存储
        
        参数:
            conversation_id: 对话ID
            source: 来源 (gemini, deepseek, chatgpt)
            user_message: 用户消息
            ai_response: AI回复
            metadata: 附加元数据
            
        返回:
            bool: 是否成功
        \"\"\"
        if not self.is_available():
            logger.warning("向量存储不可用，跳过添加对话")
            return False
        
        # 组合用户消息和AI回复作为搜索文本
        search_text = f"{user_message} {ai_response}"
        
        # 生成嵌入
        embedding = embedding_service.get_embedding(search_text)
        if not embedding:
            logger.error("生成嵌入失败，无法添加到向量存储")
            return False
        
        # 准备元数据
        doc_metadata = {
            "conversation_id": conversation_id,
            "source": source,
            "user_message": user_message[:200],  # 截断以避免过长
            "ai_response": ai_response[:200],
            "added_at": datetime.now().isoformat()
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        try:
            # 添加到向量存储
            self.collection.add(
                embeddings=[embedding],
                documents=[search_text],
                metadatas=[doc_metadata],
                ids=[str(uuid.uuid4())]
            )
            
            logger.debug(f"对话 {conversation_id} 已添加到向量存储")
            return True
            
        except Exception as e:
            logger.error(f"添加到向量存储失败: {e}")
            return False
    
    def search_similar_conversations(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.3
    ) -> List[Tuple[int, float, dict]]:
        \"\"\"
        搜索相似的对话
        
        参数:
            query: 查询文本
            limit: 返回结果数量
            min_similarity: 最小相似度阈值
            
        返回:
            List[Tuple[int, float, dict]]: (对话ID, 相似度, 元数据) 列表
        \"\"\"
        if not self.is_available():
            logger.warning("向量存储不可用，返回空结果")
            return []
        
        # 生成查询嵌入
        query_embedding = embedding_service.get_embedding(query)
        if not query_embedding:
            logger.error("生成查询嵌入失败")
            return []
        
        try:
            # 执行相似度搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["metadatas", "distances"]
            )
            
            # 处理结果
            similar_conversations = []
            if results["metadatas"] and results["distances"]:
                for metadata_list, distance_list in zip(results["metadatas"], results["distances"]):
                    for metadata, distance in zip(metadata_list, distance_list):
                        # 余弦距离转换为相似度 (1 - 距离)
                        similarity = 1.0 - distance
                        
                        if similarity >= min_similarity:
                            conversation_id = metadata.get("conversation_id")
                            if conversation_id:
                                similar_conversations.append((
                                    conversation_id,
                                    similarity,
                                    metadata
                                ))
            
            # 按相似度降序排序
            similar_conversations.sort(key=lambda x: x[1], reverse=True)
            
            logger.debug(f"语义搜索找到 {len(similar_conversations)} 个相似对话")
            return similar_conversations
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    def delete_conversation(self, conversation_id: int) -> bool:
        \"\"\"从向量存储中删除对话\"\"\"
        if not self.is_available():
            return False
        
        try:
            # 查找包含该对话ID的文档
            results = self.collection.get(
                where={"conversation_id": conversation_id}
            )
            
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.debug(f"对话 {conversation_id} 已从向量存储中删除")
                return True
            else:
                logger.debug(f"向量存储中未找到对话 {conversation_id}")
                return False
                
        except Exception as e:
            logger.error(f"从向量存储删除对话失败: {e}")
            return False
    
    def get_stats(self) -> dict:
        \"\"\"获取向量存储统计信息\"\"\"
        if not self.is_available():
            return {"available": False}
        
        try:
            count = self.collection.count()
            return {
                "available": True,
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "document_count": count,
                "storage_path": settings.CHROMA_PERSIST_DIRECTORY
            }
        except Exception as e:
            logger.error(f"获取向量存储统计失败: {e}")
            return {"available": False, "error": str(e)}

# 全局向量存储服务实例
vector_store_service = VectorStoreService()

# 便捷函数
def add_conversation_to_vector_store(conversation_id: int, source: str, user_message: str, ai_response: str):
    \"\"\"便捷函数：添加对话到向量存储\"\"\"
    return vector_store_service.add_conversation(conversation_id, source, user_message, ai_response)

def search_similar_conversations(query: str, limit: int = 10):
    \"\"\"便捷函数：搜索相似对话\"\"\"
    return vector_store_service.search_similar_conversations(query, limit)

def delete_conversation_from_vector_store(conversation_id: int):
    \"\"\"便捷函数：从向量存储删除对话\"\"\"
    return vector_store_service.delete_conversation(conversation_id)
"""
    
    write_file(base_path / "backend" / "app" / "services" / "embedding_service.py", embedding_service_content, "文本嵌入服务")
    write_file(base_path / "backend" / "app" / "services" / "vector_store.py", vector_store_content, "向量存储服务")

def create_utility_files(base_path: Path) -> None:
    """创建工具文件"""
    
    # logger.py
    logger_content = """"""
日志配置

提供统一的日志配置和管理。
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.core.config import settings

def setup_logger():
    \"\"\"设置日志配置\"\"\"
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器（滚动日志）
    file_handler = RotatingFileHandler(
        log_dir / "nexusai.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        log_dir / "nexusai_error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(log_format, date_format)
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    return root_logger

# 初始化日志
logger = setup_logger()

def get_logger(name: str = None):
    \"\"\"获取指定名称的日志记录器\"\"\"
    if name:
        return logging.getLogger(name)
    return logger
"""
    
    write_file(base_path / "backend" / "app" / "utils" / "logger.py", logger_content, "日志配置")

def create_test_files(base_path: Path) -> None:
    """创建测试文件"""
    
    # test_conversations.py
    test_content = """"""
对话API测试

测试对话相关的API端点。
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试表
Base.metadata.create_all(bind=engine)

def override_get_db():
    \"\"\"覆盖依赖注入的数据库会话\"\"\"
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# 覆盖依赖
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    \"\"\"测试健康检查端点\"\"\"
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NexusAI"

def test_create_conversation():
    \"\"\"测试创建对话\"\"\"
    conversation_data = {
        "source": "gemini",
        "user_message": "你好，请帮我写一段Python代码",
        "ai_response": "当然，这是一个简单的Python示例：print('Hello World')",
        "metadata": {"test": True}
    }
    
    response = client.post("/api/v1/conversations/", json=conversation_data)
    assert response.status_code == 201
    data = response.json()
    assert data["source"] == "gemini"
    assert data["user_message"] == conversation_data["user_message"]
    assert data["id"] is not None

def test_get_conversations():
    \"\"\"测试获取对话列表\"\"\"
    response = client.get("/api/v1/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_conversation_by_id():
    \"\"\"测试根据ID获取对话\"\"\"
    # 先创建一个对话
    conversation_data = {
        "source": "test",
        "user_message": "测试消息",
        "ai_response": "测试回复"
    }
    
    create_response = client.post("/api/v1/conversations/", json=conversation_data)
    conversation_id = create_response.json()["id"]
    
    # 获取该对话
    response = client.get(f"/api/v1/conversations/{conversation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conversation_id
    assert data["source"] == "test"

def test_search_conversations_text():
    \"\"\"测试文本搜索对话\"\"\"
    # 先创建一个包含特定关键词的对话
    conversation_data = {
        "source": "test",
        "user_message": "如何学习Python编程？",
        "ai_response": "建议从基础语法开始学习"
    }
    
    client.post("/api/v1/conversations/", json=conversation_data)
    
    # 搜索包含"Python"的对话
    search_data = {
        "query": "Python",
        "limit": 5
    }
    
    response = client.post("/api/v1/conversations/search/text", json=search_data)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    \"\"\"测试结束后清理测试数据库\"\"\"
    yield
    import os
    if os.path.exists("test.db"):
        os.remove("test.db")
"""
    
    write_file(base_path / "backend" / "tests" / "test_conversations.py", test_content, "对话API测试")

def create_root_files(base_path: Path) -> None:
    """创建根级文件"""
    
    # main.py
    main_content = """"""
NexusAI FastAPI 主应用

应用入口点，初始化FastAPI应用并注册路由。
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.utils.logger import setup_logger
from app.api.v1.endpoints import conversations, health, plugin, ollama

# 设置日志
logger = setup_logger()

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NexusAI - AI对话上下文接力系统",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(health.router, prefix="/api/v1/health", tags=["健康检查"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["对话管理"])
app.include_router(plugin.router, prefix="/api/v1/plugin", tags=["浏览器插件"])
app.include_router(ollama.router, prefix="/api/v1/ollama", tags=["Ollama集成"])

@app.get("/")
async def root():
    \"\"\"根路径\"\"\"
    return {
        "message": "欢迎使用 NexusAI API",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }

@app.on_event("startup")
async def startup_event():
    \"\"\"应用启动事件\"\"\"
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库
    from app.core.database import init_db
    init_db()
    logger.info("数据库初始化完成")
    
    # 初始化向量存储
    from app.services.vector_store import vector_store_service
    if vector_store_service.is_available():
        logger.info("向量存储初始化完成")
    else:
        logger.warning("向量存储不可用，将使用纯文本搜索")

@app.on_event("shutdown")
async def shutdown_event():
    \"\"\"应用关闭事件\"\"\"
    logger.info(f"关闭 {settings.APP_NAME}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
"""
    
    # requirements.txt
    requirements_content = """# NexusAI 项目依赖

## 核心依赖
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6

## 数据库
sqlalchemy>=2.0.0
alembic>=1.12.0

## 向量存储和嵌入
chromadb>=0.4.18
sentence-transformers>=2.2.2
numpy>=1.24.0

## HTTP客户端
httpx>=0.25.0

## 开发依赖
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
isort>=5.12.0
mypy>=1.5.0

## 其他
python-dotenv>=1.0.0
"""
    
    # .env.example
    env_example_content = """# NexusAI 环境变量配置示例

# 应用配置
APP_NAME="NexusAI"
APP_VERSION="0.1.0"
DEBUG=True

# 数据库配置
DATABASE_URL="sqlite:///./data/nexusai.db"

# ChromaDB 配置
CHROMA_PERSIST_DIRECTORY="./data/chroma_db"
CHROMA_COLLECTION_NAME="conversations"

# Embedding 模型配置
EMBEDDING_MODEL="all-MiniLM-L6-v2"

# Ollama 配置 (预留)
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="deepseek-r1:7b"

# 插件通信配置 (预留)
# PLUGIN_SECRET_KEY="your-secret-key-here"
"""
    
    write_file(base_path / "backend" / "main.py", main_content, "FastAPI应用入口点")
    write_file(base_path / "backend" / "requirements.txt", requirements_content, "Python依赖")
    write_file(base_path / "backend" / ".env.example", env_example_content, "环境变量示例")

def main():
    """主函数"""
    print("=" * 60)
    print("🛸 NexusAI 项目结构初始化脚本")
    print("=" * 60)
    print()
    
    # 获取当前工作目录
    base_path = Path.cwd()
    print(f"工作目录: {base_path}")
    print()
    
    # 确认操作
    response = input("是否在当前目录下创建 NexusAI 后端项目结构？ (y/N): ")
    if response.lower() != 'y':
        print("操作已取消")
        sys.exit(0)
    
    print()
    print("开始创建项目结构...")
    print("-" * 40)
    
    try:
        create_backend_structure(base_path)
        
        print()
        print("-" * 40)
        print("✅ 项目结构创建完成！")
        print()
        print("下一步操作：")
        print("1. 进入 backend 目录: cd backend")
        print("2. 复制环境变量: copy .env.example .env")
        print("3. 安装依赖: pip install -r requirements.txt")
        print("4. 启动开发服务器: python main.py")
        print("5. 访问 API 文档: http://localhost:8000/docs")
        print()
        print("📁 第一阶段核心文件:")
        print("  • main.py - FastAPI应用入口")
        print("  • app/core/config.py - 配置管理")
        print("  • app/core/database.py - 数据库连接")
        print("  • app/models/conversation.py - 数据模型")
        print("  • app/api/v1/endpoints/conversations.py - 对话API")
        print("  • app/services/vector_store.py - 向量存储")
        print()
        print("🔧 预留接口:")
        print("  • app/api/v1/endpoints/plugin.py - 浏览器插件API")
        print("  • app/api/v1/endpoints/ollama.py - Ollama集成API")
        
    except Exception as e:
        print(f"❌ 初始化过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()