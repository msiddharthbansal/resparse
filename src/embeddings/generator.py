from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from src.config.settings import settings

class EmbeddingGenerator:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        print("Embedding model loaded")
    
    def encode(self, text: Union[str, List[str]], batch_size: int = 32, show_progress: bool = False) -> np.ndarray:
        return self.model.encode(
            text,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
    
    def encode_query(self, query: str) -> List[float]:
        embedding = self.encode(query)
        return embedding.tolist()

embedding_generator = EmbeddingGenerator()