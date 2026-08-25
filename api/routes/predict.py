from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.schemas import RiskAssessmentRequest, RiskAssessmentResponse
from api.dependencies import get_db, get_risk_engine, get_knowledge_base
from services.risk_engine import RiskEngine
from rag.knowledge_base import KnowledgeBase
import database.crud as crud
from loguru import logger

router = APIRouter()

@router.post("/evaluate", response_model=RiskAssessmentResponse)
def evaluate_risk(
    request: RiskAssessmentRequest, 
    db: Session = Depends(get_db),
    engine: RiskEngine = Depends(get_risk_engine),
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    try:
        # Formulate a query for RAG based on the parameters to find similar historical incidents
        query_str = f"{request.attack_type} targeting {request.target_type} in {request.region} ({request.country})"
        
        # We'll pull top 5, but filter for a strict distance threshold to ensure they are actually similar
        # For simplicity, we'll just pass the top 3 closest
        historical_context = kb.search(query_str, top_k=3)
        
        # Evaluate Risk
        result = engine.evaluate_risk(request.model_dump(), historical_context=historical_context)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        # Log Prediction
        crud.log_prediction(
            db=db,
            input_data=request.model_dump(),
            predicted_threat=result['risk_level'],
            confidence=result['confidence'],
            feature_importance=result['ml_feature_importance']
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in evaluate_risk: {e}")
        raise HTTPException(status_code=500, detail=str(e))
