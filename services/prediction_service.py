import pandas as pd
import joblib
from loguru import logger
from utils.config import settings
from utils.constants import CATEGORICAL_FEATURES, NUMERIC_FEATURES

class PredictionService:
    def __init__(self):
        self.model = None
        self.encoders = {}
        self.features = CATEGORICAL_FEATURES + [f for f in NUMERIC_FEATURES if f != 'severity_score']
        self._load_assets()
        
    def _load_assets(self):
        try:
            self.model = joblib.load(settings.THREAT_MODEL_PATH)
            self.encoders = joblib.load(settings.ENCODERS_PATH)
            logger.info("ML Model and Encoders loaded successfully.")
        except FileNotFoundError:
            logger.error("Model or encoders not found. Please train the model first.")
            
    def predict(self, input_data: dict) -> dict:
        if not self.model or not self.encoders:
            return {"error": "Model not initialized."}
            
        df = pd.DataFrame([input_data])
        
        try:
            for col in CATEGORICAL_FEATURES:
                if col in df.columns:
                    classes = self.encoders[col].classes_
                    val = df[col].iloc[0]
                    if val not in classes:
                        df[col] = self.encoders[col].transform([classes[0]])
                    else:
                        df[col] = self.encoders[col].transform([val])
            
            # Ensure numeric columns exist
            for col in self.features:
                if col not in df.columns:
                    df[col] = 0.0
                    
            X = df[self.features]
            
            prediction = self.model.predict(X)[0]
            probabilities = self.model.predict_proba(X)[0]
            classes = self.model.classes_
            
            prob_dict = {str(classes[i]): float(probabilities[i]) for i in range(len(classes))}
            confidence = float(max(probabilities))
            
            # Feature Importance mapping
            importances = self.model.feature_importances_
            feature_importance = {self.features[i]: float(importances[i]) for i in range(len(self.features))}
            feature_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)[:5])
            
            return {
                "threat_level": prediction,
                "confidence": confidence,
                "probabilities": prob_dict,
                "feature_importance": feature_importance
            }
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return {"error": str(e)}
