from typing import List, Dict, Optional
from src.database.postgres import db

class DatabaseQueries:
    
    @staticmethod
    def get_categories() -> List[str]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT category_name 
                FROM journal_categories 
                ORDER BY category_name
            """)
            return [row['category_name'] for row in cursor.fetchall()]
    
    @staticmethod
    def get_top_journals_by_category(category: str, limit: int = 5) -> List[Dict]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT j.journal_id, j.journal_name, j.journal_abbr,
                       jm.jif, jm.jif_5years, jm.quartile, jm.ranking
                FROM journals j
                JOIN journal_categories jc ON j.journal_id = jc.journal_id
                JOIN journal_metrics jm ON j.journal_id = jm.journal_id
                WHERE jc.category_name = %s
                  AND jm.is_current = TRUE
                ORDER BY jm.jif DESC NULLS LAST
                LIMIT %s
            """, (category, limit))
            return cursor.fetchall()
    
    @staticmethod
    def get_latest_papers_by_journal(journal_id: int, limit: int = 10) -> List[Dict]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT paper_id, title, doi, abstract, publication_date, 
                       publication_year, volume, issue, keywords, citation_count
                FROM papers
                WHERE journal_id = %s
                  AND abstract IS NOT NULL
                  AND abstract != ''
                ORDER BY publication_date DESC NULLS LAST, paper_id DESC
                LIMIT %s
            """, (journal_id, limit))
            return cursor.fetchall()
    
    @staticmethod
    def get_paper_details(paper_id: int) -> Optional[Dict]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.*, 
                       j.journal_name, j.journal_abbr,
                       jm.jif, jm.jif_5years, jm.quartile, jm.ranking
                FROM papers p
                JOIN journals j ON p.journal_id = j.journal_id
                LEFT JOIN journal_metrics jm ON j.journal_id = jm.journal_id 
                    AND jm.is_current = TRUE
                WHERE p.paper_id = %s
            """, (paper_id,))
            return cursor.fetchone()
    
    @staticmethod
    def get_paper_authors(paper_id: int) -> List[Dict]:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.author_id, a.full_name, a.affiliation, pa.author_position
                FROM authors a
                JOIN paper_authors pa ON a.author_id = pa.author_id
                WHERE pa.paper_id = %s
                ORDER BY pa.author_position
            """, (paper_id,))
            return cursor.fetchall()

queries = DatabaseQueries()