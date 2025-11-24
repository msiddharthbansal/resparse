from typing import List, Dict
from src.embeddings.generator import embedding_generator
from src.embeddings.category_embeddings import category_embeddings

class QueryAgent:
    def __init__(self, top_k_categories: int = 3, min_category_confidence: float = 0.2):
        self.top_k_categories = top_k_categories
        self.min_category_confidence = min_category_confidence

    def process (self, query: str) -> Dict:
        query_embedding = embedding_generator.encode_query(query)
        top_categories = category_embeddings.find_similar_categories(
            query_embedding,
            top_k=self.top_k_categories
        )
        categories_raw = [
            {
                'category_name': cat_name,
                'confidence': float(score)
            }
            for cat_name, score in top_categories
        ]
        confident_categories = [
            cat for cat in categories_raw
            if cat['confidence'] >= self.min_category_confidence
        ]
        no_category_match = len(confident_categories) == 0

        if no_category_match:
            categories = [{
                'category_name': 'Uncategorized',
                'confidence': 0.0,
                'is_placeholder': True
            }]
        else:
            categories = confident_categories

        return {
            'query_text': query,
            'query_embedding': query_embedding,
            'top_categories': categories,
            'no_category_match': no_category_match
        }

query_agent = QueryAgent()