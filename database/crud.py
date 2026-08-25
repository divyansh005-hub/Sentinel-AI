from sqlalchemy.orm import Session
from database.models import Incident, PredictionHistory, QueryLog, GeneratedReport
import json
from datetime import datetime

def get_incidents(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(Incident).offset(skip).limit(limit).all()

def create_incident(db: Session, incident_data: dict):
    db_incident = Incident(**incident_data)
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

def delete_all_incidents(db: Session):
    """Clear all incident records for re-ingestion."""
    db.query(Incident).delete()
    db.commit()

def log_prediction(db: Session, input_data: dict, predicted_threat: str, confidence: float, feature_importance: dict):
    log = PredictionHistory(
        input_data=input_data,
        predicted_threat=predicted_threat,
        confidence=confidence,
        feature_importance=feature_importance
    )
    db.add(log)
    db.commit()
    return log

def save_report(db: Session, query: str, risk_level: str, file_path: str):
    report = GeneratedReport(
        query=query,
        risk_level=risk_level,
        file_path=file_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def log_query(db: Session, query_text: str, response_text: str, retrieved_incident_ids: list):
    log = QueryLog(
        query_text=query_text,
        response_text=response_text,
        retrieved_incident_ids=json.dumps(retrieved_incident_ids)
    )
    db.add(log)
    db.commit()
    return log
