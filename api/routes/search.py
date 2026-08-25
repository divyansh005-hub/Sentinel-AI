from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from api.schemas import SearchRequest, SearchResponse
from api.dependencies import get_db, get_knowledge_base
from rag.knowledge_base import KnowledgeBase
import database.crud as crud
from loguru import logger

router = APIRouter()


@router.post("/query", response_model=List[SearchResponse])
def search_incidents(
    request: SearchRequest,
    db: Session = Depends(get_db),
    kb: KnowledgeBase = Depends(get_knowledge_base)
):
    """
    Semantic vector search across the intelligence database.
    Returns enriched incident results with similarity scores.
    """
    try:
        results = kb.search(request.query, request.top_k)

        # Apply optional filters
        if request.country:
            results = [r for r in results if request.country.lower() in r.get('country', '').lower()]
        if request.region:
            results = [r for r in results if request.region.lower() in r.get('region', '').lower()]
        if request.attack_type:
            results = [r for r in results if request.attack_type.lower() in r.get('attack_type', '').lower()]
        if request.year_from or request.year_to:
            filtered = []
            for r in results:
                try:
                    year = int(str(r.get('date', ''))[:4])
                    if request.year_from and year < request.year_from:
                        continue
                    if request.year_to and year > request.year_to:
                        continue
                    filtered.append(r)
                except (ValueError, TypeError):
                    filtered.append(r)
            results = filtered

        # Log query
        retrieved_ids = [res.get('id', 0) for res in results]
        crud.log_query(db, request.query, f"{len(results)} results returned", retrieved_ids)

        # Map to response schema — ensure all required fields present
        response_items = []
        for res in results:
            response_items.append(SearchResponse(
                id=int(res.get('id', 0)),
                date=str(res.get('date', 'Unknown')),
                country=str(res.get('country', 'Unknown')),
                city=str(res.get('city', 'Unknown')),
                region=str(res.get('region', 'Unknown')),
                summary=str(res.get('summary', 'No summary available.')),
                distance=float(res.get('distance', 0.0)),
                attack_type=str(res.get('attack_type', 'Unknown')),
                fatalities=int(res.get('fatalities', 0)),
                source_dataset=str(res.get('source_dataset', 'Historical')),
            ))

        return response_items

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
