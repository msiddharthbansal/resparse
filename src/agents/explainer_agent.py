from typing import Dict
from winreg import ExpandEnvironmentStrings
from src.llm.groq_client import groq_client

class ExplainerAgent:
    def explain(self, paper: Dict, query: str) -> Dict:
        explanation = groq_client.generate_explanation(
            paper_title=paper['title'],
            query=query,
            semantic_score=paper['scores']['semantic'],
            jif=paper['scores']['jif_raw'],
            quartile=paper.get('quartile', 'N/A'),
            publication_year=paper.get('publication_year', 2025),
            journal_name=paper.get('journal_name', 'Unknown'),
            keywords=paper.get('keywords')
        )
        highlights = self._extract_highlights(paper)
        
        return {
            'explanation': explanation,
            'highlights': highlights,
            'score_breakdown': {
                'semantic': f"{paper['scores']['semantic']:.1%}",
                'journal_quality': f"JIF {paper['scores']['jif_raw']:.1f} ({paper.get('quartile', 'N/A')})",
                'recency': f"{paper['scores']['recency']:.1%}",
                'overall': f"{paper['scores']['final']:.3f}"
            }
        }
    def _extract_highlights(self, paper: Dict) -> Dict:
        return {
            'journal': f"{paper.get('journal_name', 'Unknown')} ({paper.get('quartile', 'N/A')})",
            'impact_factor': f"{paper['scores']['jif_raw']:.1f}",
            'year': paper.get('publication_year', 'N/A'),
            'relevance': f"{paper['scores']['semantic']:.0%}"
        }

explainer_agent = ExplainerAgent()