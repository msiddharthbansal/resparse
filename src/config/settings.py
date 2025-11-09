from pydantic_settings import BaseSettings
from typing import Dict
import os

class Settings (BaseSettings):
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str

    redis_host: str
    redis_port: int = 6379
    redis_password: str
    redis_db: int = 0
    
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str

    groq_api_key: str
    groq_model: str = "llama3-70b-8192"

    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    embedding_dim: int = 768

    top_categories: int = 3
    top_journals_per_category: int = 5
    latest_papers_per_journal: int = 10
    top_papers_to_rank: int = 30
    final_results_count: int = 10

    weight_semantic: float = 0.5
    weight_jif: float = 0.3
    weight_recency: float = 0.2

    cache_ttl: int = 3600
    enable_cache: bool = True

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    debug: bool = False
    log_level: str = "INFO"

    class Config:
        env_file = '.env'
        case_sensitive = False

    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def ranking_weights(self) -> Dict[str, float]:
        return {
            'semantic': self.weight_semantic,
            'jif': self.weight_jif,
            'recency': self.weight_recency
        }

settings = Settings()