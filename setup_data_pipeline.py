import os
import sys
from loguru import logger
from utils.config import settings

def setup():
    """
    Sentinel AI V2.0 Initialization Script
    Runs the unified data pipeline (GTD + ACLED), populates the database,
    and builds the FAISS vector index.
    """
    logger.info("Starting Sentinel AI V2.0 Setup...")
    
    # Ensure directories exist
    os.makedirs(settings.DATASETS_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    
    # 1. Run Data Loader (Pipeline -> SQLite)
    logger.info("Phase 1: Running Data Pipeline & Database Ingestion...")
    try:
        from services.data_loader import load_and_process_data
        success = load_and_process_data(force_rebuild=True)
        if not success:
            logger.error("Data ingestion failed. Cannot proceed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during Phase 1: {e}")
        sys.exit(1)

    # 2. Build FAISS Index
    logger.info("Phase 2: Building FAISS Vector Index...")
    try:
        from rag.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        kb_success = kb.build()
        if not kb_success:
            logger.error("Knowledge base build failed. Cannot proceed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during Phase 2: {e}")
        sys.exit(1)
        
    # 3. Train Machine Learning Model
    logger.info("Phase 3: Training Risk Engine ML Model...")
    try:
        if os.path.exists(settings.THREAT_MODEL_PATH):
            os.remove(settings.THREAT_MODEL_PATH)
        from services.ml_pipeline import MLPipeline
        pipeline = MLPipeline()
        success = pipeline.train()
        if not success or not os.path.exists(settings.THREAT_MODEL_PATH):
            logger.error("Model training failed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during Phase 3: {e}")
        sys.exit(1)
        
    logger.success("==================================================")
    logger.success("Sentinel AI V2.0 Setup Complete!")
    logger.success("==================================================")
    logger.info("You can now start the backend and frontend:")
    logger.info("1. Backend: uvicorn api.main:app --reload")
    logger.info("2. Frontend: streamlit run frontend/app.py")

if __name__ == "__main__":
    setup()
