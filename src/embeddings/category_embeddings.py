import json
from typing import Dict, List
import numpy as np
from scipy.spatial.distance import cosine


class CategoryEmbeddings:
    def __init__(self):
        self.embeddings: Dict[str, List[float]] = {}
        self.load_embeddings()
    
    def load_embeddings(self):
        with open('data/processed/category_embeddings.json', 'r') as f:
            self.embeddings = json.load(f)
        print(f"Loaded {len(self.embeddings)} category embeddings")
    
    def get_embedding(self, category: str) -> List[float]:
        return self.embeddings.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        return list(self.embeddings.keys())
    
    def find_similar_categories(self, query_embedding: List[float], top_k: int = 3) -> List[tuple]:
        similarities = []
        
        for category, cat_embedding in self.embeddings.items():
            similarity = 1 - cosine(query_embedding, cat_embedding)
            similarities.append((category, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

category_embeddings = CategoryEmbeddings()