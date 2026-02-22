"""
NexusAI FastAPI 主应用
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.utils.logger import setup_logger
from app.api.v1.endpoints import conversations, health, plugin, ollama

logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    from app.core.database import init_db
    init_db()
    yield
    # 关闭时执行
    logger.info(f"关闭 {settings.APP_NAME}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NexusAI - AI对话上下文接力系统",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gemini.google.com", "https://chat.deepseek.com"],  # 明确指定域名
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(health.router, prefix="/api/v1/health", tags=["健康检查"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["对话管理"])
app.include_router(plugin.router, prefix="/api/v1", tags=["浏览器插件"])
app.include_router(ollama.router, prefix="/api/v1/ollama", tags=["Ollama集成"])

@app.get("/")
async def root():
    return {
        "message": "欢迎使用 NexusAI API",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# 移除已弃用的 on_event 装饰器

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
