from fastapi import APIRouter, Depends, HTTPException
from api.schemas import ReportRequest, ReportResponse
from api.dependencies import get_report_generator, get_knowledge_base, get_risk_engine
from services.report_generator import ReportGenerator
from services.risk_engine import RiskEngine
from rag.knowledge_base import KnowledgeBase
from loguru import logger
import uuid

router = APIRouter()


@router.post("/generate", response_model=ReportResponse)
def generate_report(
    request: ReportRequest,
    report_gen: ReportGenerator = Depends(get_report_generator),
    kb: KnowledgeBase = Depends(get_knowledge_base),
    engine: RiskEngine = Depends(get_risk_engine)
):
    """
    Generate a comprehensive intelligence briefing report.
    If risk_assessment is not provided, the engine generates one from the query.
    """
    try:
        # 1. Retrieve relevant incidents
        incidents = kb.search(request.query, request.top_k_incidents)

        # 2. Use provided risk_assessment or generate a minimal one
        risk_assessment = request.risk_assessment
        if not risk_assessment:
            # Generate a minimal risk assessment based on query context
            risk_assessment = engine.evaluate_risk(
                incident_data={
                    "attack_type": "Unknown",
                    "target_type": "Unknown",
                    "weapon_type": "Unknown",
                    "region": "Unknown",
                    "country": "Unknown",
                    "fatalities": 0,
                    "injuries": 0,
                    "property_damage": 0.0,
                },
                historical_context=incidents
            )

        # 3. Generate the full report
        markdown_content = report_gen.generate_full_report(
            query=request.query,
            risk_assessment=risk_assessment,
            incidents=incidents
        )

        # 4. Save files
        filename = f"report_{uuid.uuid4().hex[:8]}.md"
        report_gen.save_report_markdown(markdown_content, filename)
        filepath_pdf = report_gen.save_report_pdf(markdown_content, filename)

        return ReportResponse(
            markdown_report=markdown_content,
            file_path=filepath_pdf
        )
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
