from sentence_transformers import SentenceTransformer
from loguru import logger
from utils.config import settings

class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading Embedding Model: {settings.EMBEDDING_MODEL_NAME}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def encode(self, texts: list) -> list:
        return self.model.encode(texts, show_progress_bar=False).astype('float32')
        
    def get_dimension(self) -> int:
        return self.dimension
