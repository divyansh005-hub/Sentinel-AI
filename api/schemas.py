from pydantic import BaseModel
from typing import Dict, List, Optional, Any


# ─── Prediction / Risk Assessment ────────────────────────────────────────────

class RiskAssessmentRequest(BaseModel):
    attack_type: str
    target_type: str
    weapon_type: str
    region: str
    country: str = "Unknown"
    fatalities: int = 0
    injuries: int = 0
    property_damage: float = 0.0


class RiskAssessmentResponse(BaseModel):
    risk_level: str
    confidence: float
    risk_score: int = 0
    explanation: str
    reasoning: List[str]
    risk_factors: List[str] = []
    monitoring_priority: str
    strategic_recommendations: List[str] = []
    regional_trend: str = ""
    regional_statistics: Dict[str, Any] = {}
    historical_evidence: List[dict] = []
    fatality_assessment: str = "Unknown"
    ml_feature_importance: Dict[str, float]
    supporting_incidents: List[dict] = []


# ─── Search / Incident Explorer ──────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    country: Optional[str] = None
    region: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    attack_type: Optional[str] = None
    weapon_type: Optional[str] = None
    group_name: Optional[str] = None


class SearchResponse(BaseModel):
    id: int = 0
    date: str
    country: str = "Unknown"
    city: str = "Unknown"
    region: str
    summary: str
    distance: float
    attack_type: str
    fatalities: int = 0
    source_dataset: str = "Historical"


# ─── Report Generation ────────────────────────────────────────────────────────

class ReportRequest(BaseModel):
    query: str
    risk_assessment: Optional[dict] = None  # optional — engine can generate internally
    top_k_incidents: int = 5


class ReportResponse(BaseModel):
    markdown_report: str
    file_path: str


# ─── Chat / Intelligence Copilot ─────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    query: str
    history: List[ChatMessage] = []
    top_k_incidents: int = 5


class ChatResponse(BaseModel):
    response: str
    retrieved_incidents: int
    live_mode: bool = False
    source_disclaimer: str = ""


# ─── Data & Analytics ─────────────────────────────────────────────────────────

class DataStatsResponse(BaseModel):
    total_incidents: int
    total_fatalities: int
    total_injuries: int
    countries_covered: int
    regions_covered: int
    date_range_start: str
    date_range_end: str
    source_datasets: Dict[str, int]
    top_countries: Dict[str, int]
    top_attack_types: Dict[str, int]
    high_threat_areas: Dict[str, int]
    last_updated: str


class AnalyticsRequest(BaseModel):
    chart_type: str  # 'country_ranking', 'fatality_trend', 'attack_distribution', 'regional_comparison'
    country: Optional[str] = None
    region: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    top_n: int = 10
