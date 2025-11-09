from typing import List, Dict
from src.agents.query_agents import query_agent
from src.agents.retrieval_agent import retrieval_agent
from src.agents.ranking_agent import ranking_agent
from src.agents.explainer_agent import explainer_agent
from src.database.queries import queries
from src.cache.redis_client import cache

class ResparseOrchestrator:
    def search(self, query: str, use_cache: bool = True) -> Dict:
        if use_cache:
            cached_result = cache.get_query_cache(query)
            if cached_result:
                print ("Returning the cached results!")
                cached_result['from_cache'] = True
                return cached_result

        print (f"Processing query: {query}!")
        processed_query = query_agent.process(query)

        print (f"Top Categories: {[c['category_name'] for c in processed_query['top_categories']]}")
        print ("Retrieving candidate papers!")

        candidate_papers = retrieval_agent.retrieve(processed_query)
        if not candidate_papers:
            return {
                'query': query,
                'categories': processed_query['top_categories'],
                'results': [],
                'message': 'No relevant papers found. Try broader search terms.',
                'from_cache': False
            }

        print("Ranking the papers!")
        ranked_papers = ranking_agent.rank(candidate_papers)

        print("Generating explanations now!")
        final_results = []

        for paper in ranked_papers:
            paper_details = queries.get_paper_details(paper['paper_id'])
            authors = queries.get_paper_authors(paper['paper_id'])

            explanation_data = explainer_agent.explain(paper, query)
            
            result = {
                'rank': paper['rank'],
                'paper_id': paper['paper_id'],
                'title': paper['title'],
                'doi': paper.get('doi', ''),
                'abstract': paper.get('abstract', ''),
                'authors': [
                    {
                        'name': a['full_name'],
                        'affiliation': a.get('affiliation', ''),
                        'position': a['author_position']
                    }
                    for a in authors
                ],
                'journal': {
                    'name': paper.get('journal_name', ''),
                    'abbreviation': paper_details.get('journal_abbr', '') if paper_details else '',
                    'jif': paper['scores']['jif_raw'],
                    'jif_5years': paper_details.get('jif_5years') if paper_details else None,
                    'quartile': paper.get('quartile', 'N/A'),
                    'ranking': paper.get('ranking')
                },
                'publication': {
                    'year': paper.get('publication_year'),
                    'date': str(paper.get('publication_date', '')),
                    'volume': paper.get('volume', ''),
                    'issue': paper.get('issue', '')
                },
                'keywords': paper.get('keywords', ''),
                'citation_count': paper.get('citation_count', 0),
                'pdf_url': paper.get('pdf_url', ''),
                'scores': paper['scores'],
                'explanation': explanation_data['explanation'],
                'highlights': explanation_data['highlights'],
                'score_breakdown': explanation_data['score_breakdown']
            }
            final_results.append(result)

        response = {
            'query': query,
            'categories': processed_query['top_categories'],
            'total_candidates': len(candidate_papers),
            'results': final_results,
            'from_cache': False
        }

        if use_cache:
            cache.set_query_cache(query, response)
        
        return response

orchestrator = ResparseOrchestrator()
