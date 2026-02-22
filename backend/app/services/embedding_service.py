"""
嵌入服务
"""
from typing import List, Optional

class EmbeddingService:
    def __init__(self):
        self.model = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        # 预留实现
        return [0.0] * 384 if text else None

embedding_service = EmbeddingService()
