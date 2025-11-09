from fastapi import APIRouter, HTTPException
from typing import Optional
from src.database.queries import queries

router = APIRouter(prefix="/api/papers", tags=["papers"])

@router.get("/{paper_id}")
async def get_paper_details(paper_id: int):
    try:
        paper = queries.get_paper_details(paper_id)
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        authors = queries.get_paper_authors(paper_id)
        
        return {
            "paper": dict(paper),
            "authors": [dict(a) for a in authors]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))