from typing import List, Dict
from src.database.queries import queries
from src.vectordb.pinecone_client import pinecone_client
from src.config.settings import settings

class RetrievalAgent:
    def __init__(self) -> None:
        self.top_journals_per_category = settings.top_journals_per_category
        self.latest_papers_per_journal = settings.latest_papers_per_journal
        self.top_papers_to_rank = settings.top_papers_to_rank

    def retrieve(self, processed_query: Dict) -> Dict:
        selected_journals = set()
        journal_details = {}
        categories_without_journals = []
        journals_without_papers = []

        for category_info in processed_query['top_categories']:
            category = category_info['category_name']

            top_journals = queries.get_top_journals_by_category(
                category,
                limit=self.top_journals_per_category
            )

            if not top_journals:
                categories_without_journals.append(category)
                continue

            for journal in top_journals:
                journal_id = journal['journal_id']
                if journal_id not in selected_journals:
                    selected_journals.add(journal_id)
                    journal_details[journal_id] = journal
        
        print (f"Selected {len(selected_journals)} total journals!")

        candidate_paper_ids = []
        paper_metadata = {}

        for journal_id in selected_journals:
            papers = queries.get_latest_papers_by_journal(
                journal_id, 
                limit=self.latest_papers_per_journal
            )

            if not papers:
                journals_without_papers.append(journal_details[journal_id]['journal_name'])
                continue

            for paper in papers:
                paper_id = paper['paper_id']
                candidate_paper_ids.append(paper_id)

                paper_metadata[paper_id] = {
                    **paper,
                    'journal_name': journal_details[journal_id]['journal_name'],
                    'jif': float(journal_details[journal_id]['jif'] or 0),
                    'quartile': journal_details[journal_id]['quartile'] or 'N/A',
                    'ranking': journal_details[journal_id]['ranking']
                }
        print (f"Collected {len(candidate_paper_ids)} candidate papers!")

        if not candidate_paper_ids:
            diagnostics = {
                'categories_without_journals': categories_without_journals,
                'journals_without_papers': journals_without_papers,
                'selected_journal_count': len(selected_journals)
            }
            return {
                'papers': [],
                'candidate_count': 0,
                'diagnostics': diagnostics
            }

        query_embedding = processed_query['query_embedding']
        pinecone_results = pinecone_client.query(
            embedding=query_embedding,
            top_k=500
        )

        relevant_papers = []
        for result in pinecone_results:
            paper_id = result['paper_id']
            if paper_id in paper_metadata:
                paper = {
                    **paper_metadata[paper_id],
                    'similarity_score': result['similarity_score']
                }
                relevant_papers.append(paper)
        relevant_papers.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_papers = relevant_papers[:self.top_papers_to_rank]

        print(f"Retrieved top {len(top_papers)} top papers!")

        diagnostics = {
            'categories_without_journals': categories_without_journals,
            'journals_without_papers': journals_without_papers,
            'selected_journal_count': len(selected_journals)
        }

        return {
            'papers': top_papers,
            'candidate_count': len(relevant_papers),
            'diagnostics': diagnostics
        }

retrieval_agent = RetrievalAgent()

