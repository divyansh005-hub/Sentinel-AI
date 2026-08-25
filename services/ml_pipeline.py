import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from loguru import logger
from database.sqlite_db import SessionLocal
import database.crud as crud
from utils.config import settings
from utils.constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES

class MLPipeline:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.encoders = {}
        self.features = CATEGORICAL_FEATURES + [f for f in NUMERIC_FEATURES if f != 'severity_score']
        
    def _fetch_data(self):
        db = SessionLocal()
        incidents = crud.get_incidents(db, limit=10000)
        db.close()
        
        if not incidents:
            logger.warning("No incidents found in the database.")
            return pd.DataFrame()
            
        data = []
        for i in incidents:
            severity_score = (i.fatalities * 2) + i.injuries + (i.property_damage / 10000)
            threat_level = "HIGH" if severity_score >= 15 else ("MEDIUM" if severity_score >= 5 else "LOW")
            
            row = {
                'attack_type': i.attack_type,
                'target_type': i.target_type,
                'weapon_type': i.weapon_type,
                'region': i.region,
                'country': i.country,
                'fatalities': i.fatalities,
                'injuries': i.injuries,
                'property_damage': i.property_damage,
                'threat_level': threat_level
            }
            data.append(row)
        return pd.DataFrame(data)

    def train(self):
        df = self._fetch_data()
        if df.empty:
            return False
            
        logger.info("Training ML Model...")
        
        X = df[self.features].copy()
        y = df['threat_level']
        
        for col in CATEGORICAL_FEATURES:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.encoders[col] = le
            
        self.model.fit(X, y)
        
        logger.info("Saving model and encoders...")
        joblib.dump(self.model, settings.THREAT_MODEL_PATH)
        joblib.dump(self.encoders, settings.ENCODERS_PATH)
        
        logger.success("Model training complete.")
        return True
