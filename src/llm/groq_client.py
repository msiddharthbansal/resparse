from groq import Groq
from typing import Optional
from src.config.settings import settings

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
    
    def generate_explanation(self, paper_title: str, query: str, semantic_score: float, jif: float, quartile: str, publication_year: int, journal_name: str, keywords: Optional[str] = None) -> str:
        prompt = f"""You are an academic search assistant. Explain why this research paper is relevant to the user's query in 2-3 sentences.

User Query: "{query}"

Paper Information:
- Title: {paper_title}
- Journal: {journal_name} (JIF: {jif}, Quartile: {quartile})
- Publication Year: {publication_year}
- Semantic Relevance: {semantic_score:.2%}
{f'- Keywords: {keywords}' if keywords else ''}

Provide a concise explanation covering:
1. Why it's semantically relevant to the query
2. The quality/credibility of the journal
3. The recency aspect

Keep it professional and informative. Don't use bullet points."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful academic research assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return self._generate_template_explanation(
                semantic_score, jif, quartile, publication_year
            )
    
    def _generate_template_explanation(self, semantic_score: float, jif: float, quartile: str, publication_year: int) -> str:
        if semantic_score >= 0.8:
            relevance = "highly relevant"
        elif semantic_score >= 0.6:
            relevance = "relevant"
        else:
            relevance = "somewhat relevant"
        
        if quartile == "Q1":
            quality = "top-tier"
        elif quartile == "Q2":
            quality = "high-quality"
        else:
            quality = "quality"
        
        current_year = 2025
        age = current_year - publication_year
        if age <= 1:
            recency = "very recent"
        elif age <= 2:
            recency = "recent"
        else:
            recency = f"published in {publication_year}"
        
        return (f"This paper is {relevance} to your query with a {semantic_score:.0%} semantic match. "
                f"It appears in a {quality} {quartile} journal (JIF: {jif:.1f}), ensuring high research standards. "
                f"The work is {recency}, providing current insights in the field.")

groq_client = GroqClient()