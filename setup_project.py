import os
from loguru import logger
from services.data_loader import load_and_process_data
from services.ml_pipeline import MLPipeline
from rag.knowledge_base import KnowledgeBase
from database.sqlite_db import Base, engine
from utils.config import settings

def setup_system():
    logger.info("Initializing Sentinel AI V1.0...")
    
    # Ensure DB tables exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized.")
    
    # 1. Ingest Data
    data_path = f"{settings.DATASETS_DIR}/sample_dataset.csv"
    if not load_and_process_data(data_path):
        logger.error("Data pipeline failed.")
        return

    # 2. Train ML Pipeline
    pipeline = MLPipeline()
    if not pipeline.train():
        logger.error("ML Training failed.")
        return

    # 3. Build Knowledge Base (RAG FAISS)
    kb = KnowledgeBase()
    if not kb.build():
        logger.error("Knowledge Base build failed.")
        return
        
    logger.success("Sentinel AI V1.0 Initialization Complete! Systems ready.")

if __name__ == "__main__":
    setup_system()
