"""
对话模式定义
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class ConversationBase(BaseModel):
    source: str
    user_message: str
    ai_response: str
    metadata: Optional[Any] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationInDB(ConversationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
