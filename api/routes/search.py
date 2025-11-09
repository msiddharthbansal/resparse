from fastapi import APIRouter, HTTPException
from api.schemas.request import searchRequest
from api.schemas.response import SearchResponse, ErrorResponse
from src.services.orchestrator import orchestrator

router = APIRouter(prefix="/api", tags=["search"])

@router.post("/search", response_model=SearchResponse)
async def search_papers(request: searchRequest):
    try:
        results = orchestrator.search(
            query=request.query,
            use_cache=request.use_cache
        )
        
        if request.top_n and request.top_n < len(results['results']):
            results['results'] = results['results'][:request.top_n]
        
        return results
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )