from pinecone import Pinecone
from typing import List, Dict
from time import perf_counter
from src.config.settings import settings

class PineconeClient:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index_name)
    
    def query(self, 
              embedding: List[float], 
              top_k: int = 100,
              filter_dict: Dict = None) -> List[Dict]:
        
        start = perf_counter()
        results = self.index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        duration_ms = (perf_counter() - start) * 1000
        
        papers = []
        for match in results['matches']:
            papers.append({
                'paper_id': int(match['id']),
                'similarity_score': match['score'],
                'title': match['metadata'].get('title', ''),
                'doi': match['metadata'].get('doi', ''),
                'journal_id': match['metadata'].get('journal_id'),
                'journal_name': match['metadata'].get('journal_name', ''),
                'publication_year': match['metadata'].get('publication_year'),
                'jif': match['metadata'].get('jif', 0.0),
                'quartile': match['metadata'].get('quartile', 'N/A')
            })
        print(
            "[metrics][vector_search] "
            f"top_k={top_k} duration_ms={duration_ms:.2f} "
            f"matches={len(papers)}"
        )
        return papers
    
    def get_stats(self) -> Dict:
        return self.index.describe_index_stats()

pinecone_client = PineconeClient()