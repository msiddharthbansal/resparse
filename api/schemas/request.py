from token import OP
from pydantic import BaseModel, Field, json_schema
from typing import Optional

class searchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Search query")
    top_n: Optional[int] = Field(10, ge=1, le=50, description="Number of results")
    use_cache: Optional[bool] = Field(True, description="Use cached results if available")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "continual learning in reinforcement learning",
                "top_n": 10,
                "use_cache": True
            }
        }
