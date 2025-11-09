from fastapi import APIRouter
from api.schemas.response import HealthResponse
from src.database.postgres import db
from src.cache.redis_client import cache
from src.vectordb.pinecone_client import pinecone_client
from src.config.settings import settings

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    status = {
        "status": "healthy",
        "postgres": False,
        "redis": False,
        "pinecone": False,
        "embedding_model": settings.embedding_model
    }
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT 1")
            status["postgres"] = True
    except:
        status["status"] = "degraded"
    
    try:
        cache.client.ping()
        status["redis"] = True
    except:
        status["status"] = "degraded"
    
    try:
        pinecone_client.get_stats()
        status["pinecone"] = True
    except:
        status["status"] = "degraded"
    
    return status