import pandas as pd
from loguru import logger

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features for better ML prediction."""
    logger.info("Engineering new features...")
    
    if 'fatalities' in df.columns and 'injuries' in df.columns:
        # Create a severity score
        df['severity_score'] = (df['fatalities'] * 2) + df['injuries'] + (df.get('property_damage', 0) / 10000)
    else:
        df['severity_score'] = 0.0
        
    # Generate Threat Label for training if it doesn't exist
    if 'threat_level' not in df.columns:
        df['threat_level'] = df['severity_score'].apply(
            lambda x: "HIGH" if x >= 15 else ("MEDIUM" if x >= 5 else "LOW")
        )
        
    logger.info("Feature engineering complete.")
    return df
