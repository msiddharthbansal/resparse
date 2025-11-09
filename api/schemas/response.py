from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AuthorSchema(BaseModel):
    name: str
    affiliation: str
    position: int

class JournalSchema(BaseModel):
    name: str
    abbreviation: str
    jif: float
    jif_5years: Optional[float]
    quartile: str
    ranking: Optional[int]

class PublicationSchema(BaseModel):
    year: int
    date: str
    volume: str
    issue: str

class ScoreBreakdownSchema(BaseModel):
    semantic: str
    journal_quality: str
    recency: str
    overall: str

class PaperResultSchema(BaseModel):
    rank: int
    paper_id: int
    title: str
    doi: str
    abstract: str
    authors: List[AuthorSchema]
    journal: JournalSchema
    publication: PublicationSchema
    keywords: str
    citation_count: int
    pdf_url: str
    scores: Dict[str, Any]
    explanation: str
    highlights: Dict[str, str]
    score_breakdown: ScoreBreakdownSchema

class CategorySchema(BaseModel):
    category_name: str
    confidence: float

class SearchResponse(BaseModel):
    query: str
    categories: List[CategorySchema]
    total_candidates: int
    results: List[PaperResultSchema]
    from_cache: bool
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    postgres: bool
    redis: bool
    pinecone: bool
    embedding_model: str