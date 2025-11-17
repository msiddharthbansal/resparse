from pydantic import BaseModel, field_validator
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
    year: str 
    date: str
    volume: str
    issue: str

    @field_validator("year", mode="before")
    def convert_year_to_str(cls, v):
        return str(v)

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

    @field_validator("highlights", mode="before")
    def highlights_str_values(cls, v):
        if isinstance(v, dict):
            return {k: str(val) for k, val in v.items()}
        return v

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