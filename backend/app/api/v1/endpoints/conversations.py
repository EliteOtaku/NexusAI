"""
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
