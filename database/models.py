from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from database.sqlite_db import Base
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    country = Column(String, index=True)
    city = Column(String)
    region = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    attack_type = Column(String, index=True)
    target_type = Column(String)
    weapon_type = Column(String)
    group_name = Column(String)
    fatalities = Column(Integer, default=0)
    injuries = Column(Integer, default=0)
    property_damage = Column(Float, default=0.0)
    summary = Column(Text)
    source = Column(String)
    severity_score = Column(Float)

class PredictionHistory(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_data = Column(JSON)
    predicted_threat = Column(String)
    confidence = Column(Float)
    feature_importance = Column(JSON)

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    query_text = Column(String)
    response_text = Column(Text)
    retrieved_incident_ids = Column(String) # JSON list

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    query = Column(String, index=True)
    risk_level = Column(String)
    file_path = Column(String)
