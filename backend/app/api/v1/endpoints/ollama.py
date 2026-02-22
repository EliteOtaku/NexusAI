"""
Ollama集成API (预留)
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/summarize")
async def summarize_conversation():
    return {"status": "success", "message": "预留接口"}
