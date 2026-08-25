"""
Knowledge Base — Sentinel AI V2.0
Enhanced with richer metadata storage including country, city, fatalities,
and source_dataset for enriched search results.
"""
import pickle
from loguru import logger
from rag.embedding_service import EmbeddingService
from rag.indexer import Indexer
from rag.retriever import Retriever
from database.sqlite_db import SessionLocal
import database.crud as crud
from utils.config import settings


class KnowledgeBase:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.metadata_path = settings.FAISS_INDEX_PATH.replace(".index", "_meta.pkl")
        self.metadata = []
        self._retriever = None

    def build(self):
        """Build FAISS index from all incidents in the database."""
        logger.info("Building Knowledge Base V2.0...")
        db = SessionLocal()
        incidents = crud.get_incidents(db, limit=50000)
        db.close()

        if not incidents:
            logger.warning("No incidents in database — nothing to index.")
            return False

        texts = []
        self.metadata = []
        for inc in incidents:
            # Rich text representation for better semantic matching
            text = (
                f"{inc.date} | {inc.region} | {inc.country} | {inc.city} | "
                f"{inc.attack_type} targeting {inc.target_type} | "
                f"Weapon: {inc.weapon_type} | "
                f"Fatalities: {inc.fatalities} | "
                f"{inc.summary or ''}"
            )
            texts.append(text)
            self.metadata.append({
                "id": inc.id,
                "date": str(inc.date),
                "country": str(inc.country or "Unknown"),
                "city": str(inc.city or "Unknown"),
                "region": str(inc.region or "Unknown"),
                "attack_type": str(inc.attack_type or "Unknown"),
                "target_type": str(inc.target_type or "Unknown"),
                "weapon_type": str(inc.weapon_type or "Unknown"),
                "fatalities": int(inc.fatalities or 0),
                "injuries": int(inc.injuries or 0),
                "summary": str(inc.summary or "No summary available."),
                "source_dataset": str(inc.source or "Historical"),
                "latitude": float(inc.latitude or 0.0),
                "longitude": float(inc.longitude or 0.0),
            })

        logger.info(f"Encoding {len(texts)} incidents for FAISS index...")
        indexer = Indexer(self.embedder)
        if indexer.build(texts):
            indexer.save(settings.FAISS_INDEX_PATH)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            self._retriever = None  # Reset cached retriever
            logger.success(f"Knowledge Base built: {len(texts)} incidents indexed.")
            return True
        return False

    def load_metadata(self) -> bool:
        """Load pre-built metadata from disk."""
        try:
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            logger.info(f"Loaded {len(self.metadata)} metadata entries from disk.")
            return True
        except FileNotFoundError:
            logger.warning("FAISS metadata not found — knowledge base may not be built yet.")
            return False
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return False

    def _get_retriever(self) -> Retriever:
        """Lazy-load retriever."""
        if self._retriever is None:
            self._retriever = Retriever(self.embedder, settings.FAISS_INDEX_PATH)
        return self._retriever

    def search(self, query: str, top_k: int = 5) -> list:
        """
        Perform semantic search across the intelligence database.
        Returns enriched results with similarity scores.
        """
        if not self.metadata:
            if not self.load_metadata():
                logger.warning("No metadata available — returning empty results.")
                return []

        retriever = self._get_retriever()
        if not retriever.index:
            logger.warning("FAISS index not loaded.")
            return []

        distances, indices = retriever.search(query, top_k)

        results = []
        for d, idx in zip(distances, indices):
            if idx != -1 and 0 <= idx < len(self.metadata):
                res = self.metadata[idx].copy()
                res['distance'] = float(d)
                results.append(res)

        return results
