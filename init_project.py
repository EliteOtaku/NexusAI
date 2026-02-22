#!/usr/bin/env python3
"""
NexusAI 项目初始化脚本（简化版）

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
    
    # 创建核心配置文件
    create_core_files(base_path)
    
    # 创建数据库文件
    create_database_files(base_path)
    
    # 创建API文件
    create_api_files(base_path)
    
    # 创建服务文件
    create_service_files(base_path)
    
    # 创建工具文件
    create_utility_files(base_path)
    
    # 创建根级文件
    create_root_files(base_path)

def create_core_files(base_path: Path) -> None:
    """创建核心配置文件"""
    
    # config.py
    config_content = '''"""
配置管理模块
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "NexusAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./data/nexusai.db"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "conversations"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    
    # database.py
    database_content = '''"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import conversation
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")
'''
    
    write_file(base_path / "backend" / "app" / "core" / "config.py", config_content, "配置管理")
    write_file(base_path / "backend" / "app" / "core" / "database.py", database_content, "数据库连接")

def create_database_files(base_path: Path) -> None:
    """创建数据库相关文件"""
    
    # conversation.py 模型
    model_content = '''"""
对话数据模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
'''
    
    # conversation.py 模式
    schema_content = '''"""
对话模式定义
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class ConversationBase(BaseModel):
    source: str
    user_message: str
    ai_response: str
    metadata: Optional[Any] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
'''
    
    # conversation.py CRUD
    crud_content = '''"""
对话CRUD操作
"""
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate

def create_conversation(db: Session, conversation: ConversationCreate):
    db_conversation = Conversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Conversation).offset(skip).limit(limit).all()

def get_conversation(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()
'''
    
    write_file(base_path / "backend" / "app" / "models" / "conversation.py", model_content, "对话模型")
    write_file(base_path / "backend" / "app" / "schemas" / "conversation.py", schema_content, "对话模式")
    write_file(base_path / "backend" / "app" / "crud" / "conversation.py", crud_content, "对话CRUD")

def create_api_files(base_path: Path) -> None:
    """创建API端点文件"""
    
    # conversations.py
    conversations_content = '''"""
对话API端点
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationInDB
from app.crud.conversation import create_conversation, get_conversations

router = APIRouter()

@router.post("/", response_model=ConversationInDB)
def create_conversation_endpoint(conversation: ConversationCreate, db: Session = Depends(get_db)):
    return create_conversation(db, conversation)

@router.get("/", response_model=list[ConversationInDB])
def read_conversations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_conversations(db, skip=skip, limit=limit)
'''
    
    # health.py
    health_content = '''"""
健康检查API
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
'''
    
    # plugin.py (预留)
    plugin_content = '''"""
浏览器插件API (预留)
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/conversation")
async def receive_conversation():
    return {"status": "received", "message": "预留接口"}
'''
    
    # ollama.py (预留)
    ollama_content = '''"""
Ollama集成API (预留)
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/summarize")
async def summarize_conversation():
    return {"status": "success", "message": "预留接口"}
'''
    
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "conversations.py", conversations_content, "对话API")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "health.py", health_content, "健康检查API")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "plugin.py", plugin_content, "插件API")
    write_file(base_path / "backend" / "app" / "api" / "v1" / "endpoints" / "ollama.py", ollama_content, "Ollama API")

def create_service_files(base_path: Path) -> None:
    """创建服务文件"""
    
    # embedding_service.py
    embedding_content = '''"""
嵌入服务
"""
from typing import List, Optional

class EmbeddingService:
    def __init__(self):
        self.model = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        # 预留实现
        return [0.0] * 384 if text else None

embedding_service = EmbeddingService()
'''
    
    # vector_store.py
    vector_content = '''"""
向量存储服务
"""
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
    
    def is_available(self) -> bool:
        return False
    
    def add_conversation(self, conversation_id: int, source: str, user_message: str, ai_response: str) -> bool:
        logger.info(f"预留: 添加对话 {conversation_id} 到向量存储")
        return True

vector_store_service = VectorStoreService()
'''
    
    write_file(base_path / "backend" / "app" / "services" / "embedding_service.py", embedding_content, "嵌入服务")
    write_file(base_path / "backend" / "app" / "services" / "vector_store.py", vector_content, "向量存储")

def create_utility_files(base_path: Path) -> None:
    """创建工具文件"""
    
    # logger.py
    logger_content = '''"""
日志配置
"""
import logging
import sys

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

logger = setup_logger()
'''
    
    write_file(base_path / "backend" / "app" / "utils" / "logger.py", logger_content, "日志配置")

def create_root_files(base_path: Path) -> None:
    """创建根级文件"""
    
    # main.py
    main_content = '''"""
NexusAI FastAPI 主应用
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.utils.logger import setup_logger
from app.api.v1.endpoints import conversations, health, plugin, ollama

logger = setup_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NexusAI - AI对话上下文接力系统"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1/health", tags=["健康检查"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["对话管理"])
app.include_router(plugin.router, prefix="/api/v1/plugin", tags=["浏览器插件"])
app.include_router(ollama.router, prefix="/api/v1/ollama", tags=["Ollama集成"])

@app.get("/")
async def root():
    return {
        "message": "欢迎使用 NexusAI API",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.on_event("startup")
async def startup_event():
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    from app.core.database import init_db
    init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
'''
    
    # requirements.txt
    requirements_content = '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
chromadb>=0.4.18
sentence-transformers>=2.2.2
httpx>=0.25.0
python-dotenv>=1.0.0
'''
    
    # .env.example
    env_content = '''APP_NAME="NexusAI"
APP_VERSION="0.1.0"
DEBUG=True
DATABASE_URL="sqlite:///./data/nexusai.db"
CHROMA_PERSIST_DIRECTORY="./data/chroma_db"
CHROMA_COLLECTION_NAME="conversations"
EMBEDDING_MODEL="all-MiniLM-L6-v2"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="deepseek-r1:7b"
'''
    
    write_file(base_path / "backend" / "main.py", main_content, "主应用")
    write_file(base_path / "backend" / "requirements.txt", requirements_content, "依赖文件")
    write_file(base_path / "backend" / ".env.example", env_content, "环境变量示例")

def main():
    print("=" * 60)
    print("🛸 NexusAI 项目结构初始化脚本（简化版）")
    print("=" * 60)
    print()
    
    base_path = Path.cwd()
    print(f"工作目录: {base_path}")
    print()
    
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
        print("📁 第一阶段核心文件已创建:")
        print("  • main.py - FastAPI应用入口")
        print("  • app/core/config.py - 配置管理")
        print("  • app/core/database.py - 数据库连接")
        print("  • app/models/conversation.py - 数据模型")
        print("  • app/api/v1/endpoints/conversations.py - 对话API")
        print()
        print("🔧 预留接口已创建:")
        print("  • app/api/v1/endpoints/plugin.py - 浏览器插件API")
        print("  • app/api/v1/endpoints/ollama.py - Ollama集成API")
        print("  • app/services/vector_store.py - 向量存储服务")
        
    except Exception as e:
        print(f"❌ 初始化过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()