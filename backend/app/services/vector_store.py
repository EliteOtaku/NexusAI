"""
向量存储服务
"""
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
    
    def is_available(self) -> bool:
        return False
    
    def add_conversation(self, conversation_id: int, source: str, user_message: str, ai_response: str) -> bool:
        logger.info(f"预留: 添加对话 {conversation_id} 到向量存储")
        return True

vector_store_service = VectorStoreService()
