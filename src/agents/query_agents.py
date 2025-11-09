from typing import List, Dict
from src.embeddings.generator import embedding_generator
from src.embeddings.category_embeddings import category_embeddings

class QueryAgent:
    def __init__(self, top_k_categories: int = 3):
        self.top_k_categories = top_k_categories

    def process (self, query: str) -> Dict:
        query_embedding = embedding_generator.encode_query(query)
        top_categories = category_embeddings.find_similar_categories(
            query_embedding,
            top_k=self.top_k_categories
        )
        categories = [
            {
                'category_name': cat_name,
                'confidence': float(score)
            }
            for cat_name, score in top_categories
        ]
        return {
            'query_text': query,
            'query_embedding': query_embedding,
            'top_categories': categories
        }

query_agent = QueryAgent()