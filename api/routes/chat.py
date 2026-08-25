from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ChatRequest, ChatResponse
from api.dependencies import get_knowledge_base, get_risk_engine
from services.llm_service import LLMService
from services.intelligence_ingestion import IntelligenceIngestionLayer
from rag.knowledge_base import KnowledgeBase
from loguru import logger
from database.sqlite_db import SessionLocal
import database.crud as crud

router = APIRouter()

# Singletons
llm_service = LLMService()
ingestion_layer = IntelligenceIngestionLayer()


@router.post("/", response_model=ChatResponse)
def chat_with_copilot(
    request: ChatRequest,
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    """
    Intelligence Copilot — multi-turn conversational analysis.
    Integrates RAG retrieval, live intelligence (if configured), and LLM synthesis.
    """
    try:
        logger.info(f"Copilot Query: {request.query}")

        # 1. Retrieve historical context via FAISS
        incidents = kb.search(request.query, request.top_k_incidents)

        # 2. Check for live intelligence
        live_context = ingestion_layer.get_live_context(request.query)

        # 3. Format conversation history
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]

        # 4. Generate response with all context
        response_text = llm_service.chat(
            query=request.query,
            history=history,
            context=incidents,
            live_context=live_context
        )

        # 5. Log query
        db = SessionLocal()
        try:
            retrieved_ids = [res.get('id', 0) for res in incidents]
            crud.log_query(db, request.query, response_text[:500], retrieved_ids)
        finally:
            db.close()

        return ChatResponse(
            response=response_text,
            retrieved_incidents=len(incidents),
            live_mode=ingestion_layer.is_live_mode(),
            source_disclaimer=live_context.get("disclaimer", "")
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
