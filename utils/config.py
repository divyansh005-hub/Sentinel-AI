import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentinel AI"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./database/sentinel.db"
    
    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: Optional[str] = None
    
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: str = "models/faiss.index"
    
    THREAT_MODEL_PATH: str = "models/trained_model.pkl"
    ENCODERS_PATH: str = "models/encoders.pkl"
    
    # Dataset configuration — never hardcoded filenames
    DATASETS_DIR: str = "datasets"
    GTD_DIR: str = "datasets/GTD"
    ACLED_DIR: str = "datasets/ACLED"
    PROCESSED_DIR: str = "datasets/processed"
    UNIFIED_DATASET_PATH: str = "datasets/processed/unified_intelligence.parquet"
    
    REPORTS_DIR: str = "reports/generated_reports"
    
    # Optional live intelligence APIs
    GDELT_ENABLED: bool = False
    NEWSAPI_KEY: Optional[str] = None
    NEWSAPI_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        extra = 'ignore'

settings = Settings()

# Ensure necessary directories exist
directories = [
    "models",
    settings.DATASETS_DIR,
    settings.PROCESSED_DIR,
    settings.REPORTS_DIR,
    "database",
    "logs"
]
for d in directories:
    os.makedirs(d, exist_ok=True)
