import faiss
import numpy as np
from loguru import logger
from rag.embedding_service import EmbeddingService

class Retriever:
    def __init__(self, embedder: EmbeddingService, index_path: str):
        self.embedder = embedder
        try:
            self.index = faiss.read_index(index_path)
            logger.info(f"Loaded FAISS index from {index_path}")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self.index = None
            
    def search(self, query: str, top_k: int = 5) -> tuple:
        if not self.index:
            return [], []
            
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Convert L2 distance to a pseudo-similarity score (0 to 1)
        # Assuming typical L2 distance range for these embeddings, applying a basic decay function
        scores = []
        for d in distances[0]:
            # Simple conversion: 1 / (1 + distance)
            score = 1.0 / (1.0 + float(d))
            scores.append(score)
            
        return scores, indices[0]
