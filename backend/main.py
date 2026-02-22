"""
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
