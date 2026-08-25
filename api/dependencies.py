from api.routes import data as data_routes
from database.sqlite_db import SessionLocal
from services.risk_engine import RiskEngine
from rag.knowledge_base import KnowledgeBase
from services.report_generator import ReportGenerator

# Dependency singletons — initialized once at startup
risk_engine = RiskEngine()
knowledge_base = KnowledgeBase()
report_generator = ReportGenerator()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_risk_engine() -> RiskEngine:
    return risk_engine


def get_knowledge_base() -> KnowledgeBase:
    return knowledge_base


def get_report_generator() -> ReportGenerator:
    return report_generator
