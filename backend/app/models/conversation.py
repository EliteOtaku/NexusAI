"""
对话数据模型
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    conversation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
