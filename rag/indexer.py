import faiss
import numpy as np
from loguru import logger
from rag.embedding_service import EmbeddingService
from utils.config import settings

class Indexer:
    def __init__(self, embedder: EmbeddingService):
        self.embedder = embedder
        self.index = faiss.IndexFlatL2(self.embedder.get_dimension())
        
    def build(self, texts: list):
        if not texts:
            logger.warning("No texts provided to indexer.")
            return False
            
        logger.info(f"Encoding {len(texts)} texts...")
        embeddings = self.embedder.encode(texts)
        
        logger.info("Adding to FAISS index...")
        self.index.add(embeddings)
        return True
        
    def save(self, filepath: str):
        faiss.write_index(self.index, filepath)
        logger.info(f"Index saved to {filepath}")
