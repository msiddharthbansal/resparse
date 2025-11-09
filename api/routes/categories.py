from fastapi import APIRouter, HTTPException
from src.database.queries import queries

router = APIRouter(prefix="/api", tags=["categories"])

@router.get("/categories")
async def get_all_categories():
    try:
        categories = queries.get_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))