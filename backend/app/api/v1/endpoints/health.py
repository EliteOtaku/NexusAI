"""
健康检查API
"""
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter()

async def check_ollama_service() -> dict:
    """
    检查本地 Ollama 服务状态
    
    Returns:
        dict: Ollama 服务状态信息
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 检查 Ollama API 是否可访问
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                return {
                    "status": "healthy",
                    "url": settings.OLLAMA_BASE_URL,
                    "available_models": len(models),
                    "models": [model["name"] for model in models[:5]],  # 只显示前5个模型
                    "default_model": settings.OLLAMA_MODEL,
                    "default_model_available": any(
                        model["name"] == settings.OLLAMA_MODEL for model in models
                    )
                }
            else:
                return {
                    "status": "unhealthy",
                    "url": settings.OLLAMA_BASE_URL,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "available_models": 0
                }
                
    except httpx.ConnectError:
        return {
            "status": "unreachable",
            "url": settings.OLLAMA_BASE_URL,
            "error": "无法连接到 Ollama 服务，请确保 Ollama 已启动",
            "available_models": 0
        }
    except httpx.TimeoutException:
        return {
            "status": "timeout",
            "url": settings.OLLAMA_BASE_URL,
            "error": "连接 Ollama 服务超时",
            "available_models": 0
        }
    except Exception as e:
        return {
            "status": "error",
            "url": settings.OLLAMA_BASE_URL,
            "error": f"检查 Ollama 服务时发生错误: {str(e)}",
            "available_models": 0
        }

async def check_database_connection() -> dict:
    """
    检查数据库连接状态
    
    Returns:
        dict: 数据库连接状态信息
    """
    try:
        from app.core.database import get_db
        from sqlalchemy import text
        
        # 使用同步方式检查数据库连接
        db = next(get_db())
        try:
            # 执行简单的查询测试连接
            result = db.execute(text("SELECT 1"))
            test_result = result.scalar()
            
            return {
                "status": "healthy",
                "type": "SQLite",
                "test_query_result": test_result
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "unhealthy",
            "type": "SQLite",
            "error": f"数据库连接失败: {str(e)}"
        }

@router.get("/")
async def health_check():
    """
    综合健康检查接口 - 专为 RTX 4080 优化
    
    检查项目:
    - 应用服务状态
    - Ollama 服务状态
    - 数据库连接状态
    - 硬件环境识别
    """
    # 并行检查各项服务
    ollama_status = await check_ollama_service()
    db_status = await check_database_connection()
    
    # 确定整体健康状态
    overall_status = "active"
    if ollama_status["status"] != "healthy":
        overall_status = "degraded (Ollama offline)"
    
    # 简洁响应格式，包含硬件识别锚点
    return {
        "status": overall_status,
        "service": "NexusAI Core",
        "device_target": settings.GPU_DEVICE,  # 【硬件识别锚点】
        "gpu_memory": settings.GPU_MEMORY,
        "system_memory": settings.SYSTEM_MEMORY,
        "optimization": settings.OPTIMIZATION_TARGET,
        "ollama": {
            "status": "online" if ollama_status["status"] == "healthy" else "offline",
            "models": ollama_status.get("models", [])
        },
        "database": db_status["status"] == "healthy"
    }

@router.get("/detailed")
async def health_check_detailed():
    """
    详细健康检查接口
    
    返回完整的系统状态信息
    """
    # 并行检查各项服务
    ollama_status = await check_ollama_service()
    db_status = await check_database_connection()
    
    # 确定整体健康状态
    overall_status = "healthy"
    if ollama_status["status"] != "healthy" or db_status["status"] != "healthy":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "hardware": {
            "gpu_device": settings.GPU_DEVICE,
            "gpu_memory": settings.GPU_MEMORY,
            "system_memory": settings.SYSTEM_MEMORY,
            "optimization_target": settings.OPTIMIZATION_TARGET
        },
        "components": {
            "ollama": ollama_status,
            "database": db_status
        }
    }

@router.get("/ollama")
async def ollama_health_check():
    """
    专门的 Ollama 服务健康检查
    
    返回详细的 Ollama 服务状态信息
    """
    ollama_status = await check_ollama_service()
    
    return {
        "service": "ollama",
        "status": ollama_status["status"],
        "details": ollama_status
    }

@router.get("/database")
async def database_health_check():
    """
    专门的数据库健康检查
    
    返回详细的数据库连接状态信息
    """
    db_status = await check_database_connection()
    
    return {
        "service": "database",
        "status": db_status["status"],
        "details": db_status
    }
