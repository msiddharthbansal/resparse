from fastapi import APIRouter, HTTPException
from api.schemas.request import searchRequest
from api.schemas.response import SearchResponse
from src.services.orchestrator import orchestrator
import math
from decimal import Decimal

router = APIRouter(prefix="/api", tags=["search"])

def sanitize(obj):
    if isinstance(obj, Decimal):
        obj = float(obj)

    if isinstance(obj, float):
        if math.isinf(obj) or math.isnan(obj):
            return None
        return obj

    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [sanitize(v) for v in obj]

    return obj


@router.post("/search", response_model=SearchResponse)
async def search_papers(request: searchRequest):
    try:
        results = orchestrator.search(
            query=request.query,
            use_cache=request.use_cache
        )

        if request.top_n and request.top_n < len(results["results"]):
            results["results"] = results["results"][: request.top_n]

        results = sanitize(results)

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
