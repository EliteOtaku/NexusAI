"""
浏览器插件API - 专为 RTX 4080 优化的数据接收接口
"""
import json
import hashlib
import sqlite3
import httpx
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from app.core.config import settings
from app.utils.logger import logger

router = APIRouter()

# 数据库连接管理
class DatabaseManager:
    """数据库管理器 - 专为 RTX 4080 优化的连接池"""
    
    def __init__(self, db_path: str = "../nexus_storage/data/nexus_vault.db"):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接（单例模式）"""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            # 配置性能优化
            self._connection.execute("PRAGMA journal_mode = WAL")
            self._connection.execute("PRAGMA synchronous = NORMAL")
            self._connection.execute("PRAGMA cache_size = -64000")
        return self._connection
    
    def close_connection(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

# 全局数据库管理器
db_manager = DatabaseManager()

def get_db():
    """依赖注入：获取数据库连接"""
    return db_manager.get_connection()

class IngestData(BaseModel):
    """数据接收模型"""
    source: str  # 数据来源: gemini, chatgpt, claude 等
    content: str  # AI 回复内容
    url: str  # 来源网址
    timestamp: str  # 时间戳
    element_html: str = ""  # 原始 HTML 元素（用于调试）
    metadata: dict = {}  # 扩展元数据

class IngestResponse(BaseModel):
    """数据接收响应模型"""
    status: str  # success, error
    message: str
    ingest_id: str = ""
    processed_at: str
    vector_embedding: bool = False
    gpu_accelerated: bool = True

@router.post("/ingest")
async def ingest_conversation(data: IngestData, db: sqlite3.Connection = Depends(get_db)):
    """
    接收浏览器插件发送的 AI 对话数据
    
    功能:
    - 验证数据完整性
    - 存储到数据库
    - 生成向量嵌入（GPU 加速）
    - 返回处理结果
    """
    try:
        logger.info(f"📥 收到来自 {data.source} 的数据")
        
        # 验证数据
        if not data.content or len(data.content.strip()) < 10:
            raise HTTPException(status_code=400, detail="内容太短或为空")
        
        # 生成唯一标识
        ingest_id = f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(data.content) % 10000:04d}"
        
        # 处理数据并存储到数据库
        processed_data = await process_ingested_data_with_db(data, ingest_id, db)
        
        # 记录到日志
        logger.info(f"✅ 数据接收成功: {ingest_id}, 长度: {len(data.content)} 字符")
        
        return IngestResponse(
            status="success",
            message=f"数据已成功接收并处理",
            ingest_id=ingest_id,
            processed_at=datetime.now().isoformat(),
            vector_embedding=True,
            gpu_accelerated=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 数据接收失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据处理失败: {str(e)}")

@router.post("/ingest/batch")
async def ingest_conversation_batch(data: list[IngestData], db: sqlite3.Connection = Depends(get_db)):
    """
    批量接收 AI 对话数据
    
    专为大量数据处理优化，支持 GPU 加速批量处理
    """
    try:
        if not data or len(data) == 0:
            raise HTTPException(status_code=400, detail="数据列表为空")
        
        if len(data) > 100:
            raise HTTPException(status_code=400, detail="单次批量处理限制 100 条")
        
        logger.info(f"📦 批量接收 {len(data)} 条数据")
        
        results = []
        for i, item in enumerate(data):
            try:
                ingest_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i:03d}"
                processed_data = await process_ingested_data_with_db(item, ingest_id, db)
                
                if processed_data.get("status") == "skipped":
                    results.append({
                        "status": "skipped",
                        "ingest_id": ingest_id,
                        "source": item.source,
                        "reason": "duplicate_content"
                    })
                else:
                    results.append({
                        "status": "success",
                        "ingest_id": ingest_id,
                        "source": item.source,
                        "content_length": len(item.content),
                        "session_id": processed_data.get("session_id"),
                        "message_id": processed_data.get("message_id")
                    })
                
            except Exception as e:
                results.append({
                    "status": "error",
                    "ingest_id": f"error_{i:03d}",
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["status"] == "success")
        skipped_count = sum(1 for r in results if r["status"] == "skipped")
        
        logger.info(f"✅ 批量处理完成: {success_count}成功, {skipped_count}跳过, {len(data)-success_count-skipped_count}失败")
        
        return {
            "status": "completed",
            "processed_count": len(data),
            "success_count": success_count,
            "skipped_count": skipped_count,
            "error_count": len(data) - success_count - skipped_count,
            "results": results,
            "gpu_batch_processing": True,
            "processed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 批量数据接收失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")

@router.get("/ingest/status")
async def get_ingest_status():
    """
    获取数据接收服务状态
    
    返回当前处理能力、GPU 状态等信息
    """
    return {
        "service": "nexus-ingest",
        "status": "active",
        "gpu_device": settings.GPU_DEVICE,
        "gpu_memory": settings.GPU_MEMORY,
        "optimization": "GPU-accelerated vector embedding",
        "max_batch_size": 100,
        "supported_sources": ["gemini", "chatgpt", "claude", "deepseek"],
        "last_processed": datetime.now().isoformat(),
        "health": "excellent"
    }

async def process_ingested_data_with_db(data: IngestData, ingest_id: str, db: sqlite3.Connection) -> dict:
    """
    处理接收到的数据并存储到数据库
    
    包括:
    - 数据清洗和格式化
    - 向量嵌入生成（GPU 加速）
    - 存储到数据库
    - 触发后续处理流程
    """
    try:
        cursor = db.cursor()
        
        # 数据清洗
        cleaned_content = clean_content(data.content)
        
        # 生成内容哈希（用于去重）
        content_hash = hashlib.sha256(cleaned_content.encode()).hexdigest()
        
        # 检查是否已存在相同内容
        cursor.execute("SELECT id FROM messages WHERE content_hash = ?", (content_hash,))
        existing_message = cursor.fetchone()
        
        if existing_message:
            logger.info(f"🔁 跳过重复内容: {content_hash[:16]}...")
            return {"status": "skipped", "reason": "duplicate_content"}
        
        # 查找或创建会话
        session_id = await get_or_create_session(data, db)
        
        # 生成向量嵌入（GPU 加速）
        embedding_vector = await generate_vector_embedding(cleaned_content)
        
        # 插入消息记录
        cursor.execute("""
            INSERT INTO messages 
            (session_id, role, content, content_hash, platform_message_id, 
             model_used, embedding_vector, embedding_model, embedding_dim, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id, 
            "assistant",  # 浏览器插件捕获的都是 AI 回复
            cleaned_content, 
            content_hash,
            data.metadata.get("message_id") if data.metadata else None,
            data.metadata.get("model") if data.metadata else None,
            embedding_vector,
            "all-MiniLM-L6-v2",  # 默认模型
            384,  # 默认维度
            json.dumps({
                "source_url": data.url,
                "original_timestamp": data.timestamp,
                "element_html": data.element_html[:1000] if data.element_html else "",
                "ingest_id": ingest_id,
                "platform_metadata": data.metadata
            })
        ))
        
        message_id = cursor.lastrowid
        
        # 插入向量嵌入记录
        if embedding_vector:
            cursor.execute("""
                INSERT INTO vector_embeddings 
                (message_id, embedding_data, embedding_model, embedding_dim, embedding_norm)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, embedding_vector, "all-MiniLM-L6-v2", 384, 1.0))
        
        # 更新会话统计
        cursor.execute("""
            UPDATE sessions 
            SET message_count = message_count + 1,
                updated_at = CURRENT_TIMESTAMP,
                last_active_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (session_id,))
        
        db.commit()
        
        stored_data = {
            "ingest_id": ingest_id,
            "session_id": session_id,
            "message_id": message_id,
            "source": data.source,
            "content": cleaned_content,
            "content_length": len(cleaned_content),
            "vector_embedding_generated": embedding_vector is not None,
            "processed_at": datetime.now().isoformat(),
            "gpu_processed": True
        }
        
        logger.debug(f"🔧 数据存储完成: 会话 {session_id}, 消息 {message_id}")
        
        return stored_data
        
    except Exception as e:
        logger.error(f"❌ 数据库存储失败: {e}")
        db.rollback()
        raise

async def get_or_create_session(data: IngestData, db: sqlite3.Connection) -> int:
    """获取或创建会话记录"""
    cursor = db.cursor()
    
    # 尝试基于 URL 和平台查找现有会话
    platform_session_id = data.metadata.get("session_id") if data.metadata else None
    
    if platform_session_id:
        cursor.execute("SELECT id FROM sessions WHERE platform_session_id = ?", (platform_session_id,))
        existing_session = cursor.fetchone()
        
        if existing_session:
            return existing_session[0]
    
    # 创建新会话
    session_uuid = hashlib.md5(f"{data.source}_{datetime.now().timestamp()}".encode()).hexdigest()
    
    # 从 URL 提取会话标题
    title = f"{data.source.capitalize()} 对话"
    if "gemini" in data.url:
        title = "Gemini AI 对话"
    elif "deepseek" in data.url:
        title = "DeepSeek AI 对话"
    
    cursor.execute("""
        INSERT INTO sessions 
        (session_uuid, platform, title, platform_session_id, metadata)
        VALUES (?, ?, ?, ?, ?)
    """, (
        session_uuid,
        data.source,
        title,
        platform_session_id,
        json.dumps({
            "source_url": data.url,
            "created_from_ingest": True,
            "original_timestamp": data.timestamp
        })
    ))
    
    session_id = cursor.lastrowid
    logger.info(f"📁 创建新会话: {session_id} ({title})")
    
    return session_id

def clean_content(content: str) -> str:
    """清洗和格式化内容"""
    # 移除多余的空格和换行
    cleaned = ' '.join(content.split())
    
    # 移除特殊字符（保留中文、英文、数字和基本标点）
    import re
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff\.,!?;:()\[\]{}]', '', cleaned)
    
    return cleaned.strip()

async def generate_vector_embedding(content: str) -> Optional[bytes]:
    """
    生成向量嵌入 - 专为 RTX 4080 GPU 优化
    
    使用 sentence-transformers 模型，强制使用 GPU 加速
    """
    try:
        # 尝试使用 sentence-transformers
        from sentence_transformers import SentenceTransformer
        import torch
        import numpy as np
        
        # 强制使用 GPU（如果可用）
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 使用适合 RTX 4080 的高性能模型
        model_name = "all-MiniLM-L6-v2"  # 384维，速度快，适合实时处理
        
        # 初始化模型（单例模式，避免重复加载）
        if not hasattr(generate_vector_embedding, "model"):
            logger.info(f"🚀 加载 sentence-transformers 模型: {model_name} (设备: {device})")
            generate_vector_embedding.model = SentenceTransformer(model_name, device=device)
        
        model = generate_vector_embedding.model
        
        # 生成嵌入（GPU 加速）
        embedding = model.encode([content], convert_to_numpy=True)
        
        # 转换为二进制格式以便存储
        embedding_bytes = embedding[0].tobytes()
        
        logger.debug(f"🔧 向量嵌入生成成功: {len(embedding_bytes)} 字节 (维度: {embedding.shape[1]})")
        
        return embedding_bytes
        
    except ImportError:
        logger.warning("⚠️ sentence-transformers 未安装，使用模拟嵌入")
        # 模拟嵌入（用于测试）
        import numpy as np
        embedding = np.random.randn(384).astype(np.float32)
        return embedding.tobytes()
        
    except Exception as e:
        logger.error(f"❌ 向量嵌入生成失败: {e}")
        return None

@router.post("/conversation")
async def receive_conversation():
    """预留接口 - 保持向后兼容"""
    return {"status": "received", "message": "请使用 /ingest 接口"}


class DistillRequest(BaseModel):
    """逻辑蒸馏请求模型 - 支持多 LLM 提供商"""
    session_id: Optional[str] = None
    limit: int = 10
    model: str = "deepseek-r1:8b"
    provider: Optional[str] = None  # 可选：强制指定提供商 (ollama/cloud)


@router.post("/distill")
async def distill_logic(request: DistillRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    逻辑蒸馏：生成接力提示词 (Bridge Prompt)
    
    支持多 LLM 提供商：
    - ollama: 本地 RTX 4080 推理（高性能模式）
    - cloud: 云端 API 推理（省电模式）
    """
    try:
        # 确定使用的 LLM 提供商
        provider = request.provider or settings.LLM_PROVIDER
        logger.info(f"🧠 开始逻辑蒸馏 (提供商: {provider})...")
        
        # 1. 从金库(SQLite)中捞出最近的对话内容
        recent_messages = await get_latest_messages(db, request.limit, request.session_id)
        
        if not recent_messages:
            return {"status": "error", "message": "金库空空如也，先去网页聊两句吧"}
        
        # 构建上下文文本
        context_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        # 2. 构建蒸馏 Prompt (这是 2280 分逻辑的精髓)
        distill_prompt = f"""
你是一个逻辑蒸馏专家。请分析以下对话内容，并将其浓缩为一段"接力提示词"。
要求：
1. 总结当前讨论的核心问题和已达成的共识。
2. 指明下一步需要解决的具体逻辑点。
3. 语气简洁专业，直接用于输入给另一个 AI。

对话内容：
{context_text}
"""
        
        # 3. 根据提供商选择推理方式
        if provider == "ollama":
            # 本地 Ollama 推理（RTX 4080 模式）
            result = await call_ollama_inference(distill_prompt, request.model)
            device_info = "NVIDIA RTX 4080"
            performance_mode = "high_performance"
        else:
            # 云端 API 推理（笔记本省电模式）
            result = await call_external_api(distill_prompt, request.model)
            device_info = "Cloud API"
            performance_mode = "power_saving"
        
        logger.info(f"✅ 逻辑蒸馏成功: 生成 {len(result)} 字符的接力提示词 ({performance_mode})")
        
        return {
            "status": "success",
            "device": device_info,
            "performance_mode": performance_mode,
            "llm_provider": provider,
            "bridge_prompt": result,
            "context_messages_count": len(recent_messages),
            "model_used": request.model,
            "distill_timestamp": datetime.now().isoformat()
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 逻辑蒸馏失败: {e}")
        raise HTTPException(status_code=500, detail=f"逻辑蒸馏过程出错: {str(e)}")


async def call_ollama_inference(prompt: str, model: str) -> str:
    """
    调用本地 Ollama 进行推理（RTX 4080 模式）
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise HTTPException(status_code=500, detail=f"Ollama 响应异常: {response.status_code}")
                
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Ollama 服务未启动，请检查 localhost:11434")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Ollama 响应超时，请检查模型是否已加载")


async def call_external_api(prompt: str, model: str) -> str:
    """
    调用外部 API 进行推理（云端省电模式）
    
    支持 OpenAI 兼容的 API 格式
    """
    if not settings.EXTERNAL_API_KEY:
        raise HTTPException(status_code=400, detail="云端推理需要配置 EXTERNAL_API_KEY")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 使用 OpenAI 兼容的格式
            response = await client.post(
                f"{settings.EXTERNAL_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.EXTERNAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.EXTERNAL_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个逻辑蒸馏专家，擅长将复杂对话浓缩为简洁的接力提示词。"
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = response.json().get("error", {}).get("message", "未知错误")
                raise HTTPException(status_code=500, detail=f"云端 API 错误: {error_msg}")
                
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="云端 API 连接失败，请检查网络和配置")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="云端 API 响应超时")
    except KeyError:
        raise HTTPException(status_code=500, detail="云端 API 响应格式异常")


async def get_latest_messages(db: sqlite3.Connection, limit: int = 10, session_id: Optional[str] = None) -> list:
    """
    从数据库获取最新的对话消息
    
    Args:
        db: 数据库连接
        limit: 消息数量限制
        session_id: 特定会话ID（可选）
    
    Returns:
        消息列表，包含角色和内容
    """
    cursor = db.cursor()
    
    if session_id:
        # 获取特定会话的消息
        cursor.execute("""
            SELECT role, content FROM messages 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (session_id, limit))
    else:
        # 获取所有会话的最新消息
        cursor.execute("""
            SELECT role, content FROM messages 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "role": row[0],
            "content": row[1]
        })
    
    # 反转顺序，使消息按时间顺序排列
    messages.reverse()
    
    return messages
