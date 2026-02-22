"""
对话CRUD操作
"""
from sqlalchemy.orm import Session
from app.models.conversation import Message
from app.schemas.conversation import ConversationCreate

def create_conversation(db: Session, conversation: ConversationCreate):
    db_conversation = Message(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Message).offset(skip).limit(limit).all()

def get_conversation(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.id == conversation_id).first()
