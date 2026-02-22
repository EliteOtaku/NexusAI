"""
浏览器插件API (预留)
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/conversation")
async def receive_conversation():
    return {"status": "received", "message": "预留接口"}
