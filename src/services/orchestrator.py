from typing import List, Dict, Optional
from urllib.parse import quote_plus
from time import perf_counter
from src.agents.query_agents import query_agent
from src.agents.retrieval_agent import retrieval_agent
from src.agents.ranking_agent import ranking_agent
from src.agents.explainer_agent import explainer_agent
from src.database.queries import queries
from src.cache.redis_client import cache

class ResparseOrchestrator:
    def __init__(self) -> None:
        self.scholar_base_url = "https://scholar.google.com/scholar?q="

    def _build_google_scholar_url(self, query: str) -> str:
        return f"{self.scholar_base_url}{quote_plus(query)}"

    def _no_results_response(
        self,
        query: str,
        categories: List[Dict],
        message: str,
        diagnostics: Optional[Dict] = None
    ) -> Dict:
        return {
            'query': query,
            'categories': categories,
            'total_candidates': 0,
            'results': [],
            'message': message,
            'fallback_url': self._build_google_scholar_url(query),
            'diagnostics': diagnostics or {},
            'from_cache': False
        }

    def search(self, query: str, use_cache: bool = True) -> Dict:
        request_start = perf_counter()
        cache_lookup_ms = None
        cache_hit = False
        cached_compute_ms = None

        if use_cache:
            cache_start = perf_counter()
            cached_result = cache.get_query_cache(query)
            cache_lookup_ms = (perf_counter() - cache_start) * 1000
            if cached_result:
                cache_hit = True
                cached_compute_ms = (
                    cached_result
                    .get('diagnostics', {})
                    .get('timing', {})
                    .get('compute_ms')
                )
                total_ms = (perf_counter() - request_start) * 1000
                print(
                    "[metrics][cache] hit "
                    f"query='{query}' "
                    f"lookup_ms={cache_lookup_ms:.2f} "
                    f"saved_compute_ms={cached_compute_ms if cached_compute_ms is not None else 'n/a'} "
                    f"total_ms={total_ms:.2f}"
                )
                cached_result['from_cache'] = True
                return cached_result

        print (f"Processing query: {query}!")
        processing_start = perf_counter()
        processed_query = query_agent.process(query)
        processing_ms = (perf_counter() - processing_start) * 1000

        if processed_query.get('no_category_match'):
            total_ms = (perf_counter() - request_start) * 1000
            print(
                "[metrics][query] no_category_match "
                f"query='{query}' total_ms={total_ms:.2f} "
                f"cache_lookup_ms={cache_lookup_ms if cache_lookup_ms is not None else 0:.2f} "
                f"processing_ms={processing_ms:.2f}"
            )
            return self._no_results_response(
                query=query,
                categories=processed_query['top_categories'],
                message='We could not match your query to any known research categories. Try a broader description or different terms.',
                diagnostics={'reason': 'no_category_match'}
            )

        print (f"Top Categories: {[c['category_name'] for c in processed_query['top_categories']]}")
        print ("Retrieving candidate papers!")

        retrieval_start = perf_counter()
        retrieval_output = retrieval_agent.retrieve(processed_query)
        retrieval_ms = (perf_counter() - retrieval_start) * 1000
        candidate_papers = retrieval_output['papers']
        diagnostics = retrieval_output.get('diagnostics', {})
        total_candidates = retrieval_output.get('candidate_count', len(candidate_papers))

        if not candidate_papers:
            total_ms = (perf_counter() - request_start) * 1000
            print(
                "[metrics][query] no_candidates "
                f"query='{query}' total_ms={total_ms:.2f} "
                f"processing_ms={processing_ms:.2f} "
                f"retrieval_ms={retrieval_ms:.2f}"
            )
            message = self._compose_no_results_message(diagnostics)
            return self._no_results_response(
                query=query,
                categories=processed_query['top_categories'],
                message=message,
                diagnostics=diagnostics
            )

        print("Ranking the papers!")
        ranking_start = perf_counter()
        ranked_papers = ranking_agent.rank(candidate_papers)
        ranking_ms = (perf_counter() - ranking_start) * 1000

        print("Generating explanations now!")
        explanation_start = perf_counter()
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
        explanation_ms = (perf_counter() - explanation_start) * 1000

        response = {
            'query': query,
            'categories': processed_query['top_categories'],
            'total_candidates': total_candidates,
            'results': final_results,
            'message': None,
            'fallback_url': None,
            'diagnostics': diagnostics,
            'from_cache': False
        }

        total_ms = (perf_counter() - request_start) * 1000
        compute_ms = total_ms - (cache_lookup_ms or 0)

        response['diagnostics'] = {
            **diagnostics,
            'timing': {
                'total_ms': total_ms,
                'cache_lookup_ms': cache_lookup_ms,
                'processing_ms': processing_ms,
                'retrieval_ms': retrieval_ms,
                'ranking_ms': ranking_ms,
                'explanation_ms': explanation_ms,
                'compute_ms': compute_ms
            }
        }

        print(
            "[metrics][query] completed "
            f"query='{query}' total_ms={total_ms:.2f} "
            f"compute_ms={compute_ms:.2f} "
            f"processing_ms={processing_ms:.2f} "
            f"retrieval_ms={retrieval_ms:.2f} "
            f"ranking_ms={ranking_ms:.2f} "
            f"explanation_ms={explanation_ms:.2f}"
        )

        if use_cache and not cache_hit:
            print(
                "[metrics][cache] miss "
                f"query='{query}' lookup_ms={cache_lookup_ms if cache_lookup_ms is not None else 0:.2f} "
                f"compute_ms={compute_ms:.2f} "
                f"total_ms={total_ms:.2f}"
            )

        if use_cache:
            cache.set_query_cache(query, response)
        
        return response

    def _compose_no_results_message(self, diagnostics: Dict) -> str:
        categories_without_journals = diagnostics.get('categories_without_journals', [])
        journals_without_papers = diagnostics.get('journals_without_papers', [])

        if categories_without_journals:
            return (
                "None of the matched categories currently have indexed journals "
                f"({', '.join(categories_without_journals)})."
            )

        if journals_without_papers:
            return (
                "The journals we checked do not have recent papers available. "
                "Try expanding your search scope."
            )

        return 'No relevant papers found. Try broader search terms.'

orchestrator = ResparseOrchestrator()
