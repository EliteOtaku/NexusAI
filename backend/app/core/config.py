"""
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
