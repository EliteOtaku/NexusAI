"""
配置管理模块 - 支持多 LLM 提供商（降维打击模式）
"""
from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    APP_NAME: str = "NexusAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./data/nexusai.db"
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "conversations"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # LLM 提供商配置（支持本地和云端）
    LLM_PROVIDER: Literal['ollama', 'cloud'] = 'ollama'  # ollama: 本地推理, cloud: 云端推理
    
    # Ollama 配置（RTX 4080 模式）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:8b"
    
    # 云端 API 配置（笔记本省电模式）
    EXTERNAL_API_BASE: str = "https://api.openai.com/v1"
    EXTERNAL_API_KEY: str = ""
    EXTERNAL_MODEL: str = "gpt-3.5-turbo"
    
    # 硬件配置（专为 RTX 4080 优化）
    GPU_DEVICE: str = "NVIDIA RTX 4080"
    GPU_MEMORY: str = "16GB GDDR6X"
    SYSTEM_MEMORY: str = "128GB DDR5"
    OPTIMIZATION_TARGET: str = "GPU-accelerated AI inference"
    
    # 性能模式配置
    PERFORMANCE_MODE: Literal['high_performance', 'power_saving'] = 'high_performance'
    
    class Config:
        env_file = ".env"

settings = Settings()
