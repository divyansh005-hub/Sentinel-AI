import pandas as pd
from loguru import logger
from utils.constants import NUMERIC_FEATURES, CATEGORICAL_FEATURES

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values and basic cleaning."""
    logger.info("Starting data preprocessing...")
    
    # Fill numeric
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)
            
    # Fill categorical
    for col in CATEGORICAL_FEATURES:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
            
    # Drop rows without dates
    if 'date' in df.columns:
        df = df.dropna(subset=['date'])
        
    logger.info(f"Data cleaning complete. Shape: {df.shape}")
    return df
