from typing import List, Dict
from src.config.settings import settings
from src.utils.normalization import normalize_jif, calculate_recency_score

class RankingAgent:
    def __init__(self) -> None:
        self.weights = settings.ranking_weights
        self.current_year = 2025
        self.max_jif = 100.0

    def rank(self, papers: List[Dict], top_n: int = None) -> List[Dict]:
        if top_n is None:
            top_n = settings.final_results_count
        
        scored_papers = []
        for paper in papers:
            semantic_score = paper.get('similarity_score', 0.0)
            jif = paper.get('jif', 0.0)
            pub_year = paper.get('publication_year', self.current_year)
            
            jif_score = normalize_jif(jif, self.max_jif)
            recency_score = calculate_recency_score(pub_year, self.current_year)
            
            final_score = (
                self.weights['semantic'] * semantic_score +
                self.weights['jif'] * jif_score +
                self.weights['recency'] * recency_score
            )
            
            paper['scores'] = {
                'semantic': semantic_score,
                'jif_raw': jif,
                'jif_normalized': jif_score,
                'recency': recency_score,
                'final': final_score
            }
            
            scored_papers.append(paper)
        scored_papers.sort(key=lambda x: x['scores']['final'], reverse=True)
        
        for i, paper in enumerate(scored_papers[: top_n]):
            paper['rank'] = i +1
        return scored_papers[: top_n]

ranking_agent = RankingAgent()