import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)

def load_journals():
    df = pd.read_csv('data/raw/journals.csv')
    data = [(r['journal_name'], r['journal_abbr'], r['journal_url']) 
            for _, r in df.iterrows()]
    
    cursor = conn.cursor()
    execute_batch(cursor, """
        INSERT INTO journals (journal_name, journal_abbr, journal_url)
        VALUES (%s, %s, %s)
        ON CONFLICT (journal_name) DO NOTHING
    """, data)
    conn.commit()
    cursor.close()
    print(f"Loaded {len(data)} journals")

def load_journal_metrics():
    df = pd.read_csv('data/raw/journal_metrics.csv')
    data = [(r['journal_id'], r['year'], r['jif'], r['jif_5years'], 
             r['quartile'], r['ranking'], r['year'] == 2024)
            for _, r in df.iterrows()]
    
    cursor = conn.cursor()
    execute_batch(cursor, """
        INSERT INTO journal_metrics 
        (journal_id, year, jif, jif_5years, quartile, ranking, is_current)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (journal_id, year) DO UPDATE
        SET jif = EXCLUDED.jif, quartile = EXCLUDED.quartile
    """, data)
    conn.commit()
    cursor.close()
    print(f"Loaded {len(data)} journal metrics")

def load_journal_categories():
    df = pd.read_csv('data/raw/journal_categories.csv')
    data = [(r['journal_id'], r['category_name']) for _, r in df.iterrows()]
    
    cursor = conn.cursor()
    execute_batch(cursor, """
        INSERT INTO journal_categories (journal_id, category_name)
        VALUES (%s, %s)
        ON CONFLICT (journal_id, category_name) DO NOTHING
    """, data)
    conn.commit()
    cursor.close()
    print(f"Loaded {len(data)} categories")

def load_papers():
    df = pd.read_csv('data/raw/papers.csv')

    data = [(r['title'], r['doi'], r['journal_id'], r['publication_date'],
             r['publication_year'], r['volume'], r['issue'], r['abstract'],
             r['keywords'], r['pdf_url'], r['citation_count'])
            for _, r in df.iterrows()]
    
    cursor = conn.cursor()
    execute_batch(cursor, """
        INSERT INTO papers 
        (title, doi, journal_id, publication_date, publication_year,
         volume, issue, abstract, keywords, pdf_url, citation_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (doi) DO NOTHING
    """, data, page_size=100)

    conn.commit()
    cursor.close()
    print(f"Loaded {len(data)} papers")

def load_authors():
    df = pd.read_csv('data/raw/authors.csv')
    data = [(r['full_name'], r['affiliation']) for _, r in df.iterrows()]
    
    cursor = conn.cursor()
    execute_batch(cursor, """
        INSERT INTO authors (full_name, affiliation)
        VALUES (%s, %s)
    """, data)
    conn.commit()
    cursor.close()
    print(f"Loaded {len(data)} authors")

def load_paper_authors():
    paper_authors_df = pd.read_csv('data/raw/paper_authors.csv')
    papers_df = pd.read_csv('data/raw/papers.csv')
    authors_df = pd.read_csv('data/raw/authors.csv')
    
    csv_paper_id_to_doi = dict(zip(papers_df['paper_id'], papers_df['doi']))
    csv_author_id_to_name = dict(zip(authors_df['author_id'], authors_df['full_name']))
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT paper_id, doi FROM papers")
    doi_to_paper_id = {doi: paper_id for paper_id, doi in cursor.fetchall()}
    
    cursor.execute("SELECT author_id, full_name FROM authors")
    name_to_author_id = {full_name: author_id for author_id, full_name in cursor.fetchall()}
    
    data = []
    for _, row in paper_authors_df.iterrows():
        csv_paper_id = int(row['paper_id'])
        csv_author_id = int(row['author_id'])
        author_position = int(row['author_position'])
        
        # Get DOI and author name from mappings
        doi = csv_paper_id_to_doi.get(csv_paper_id)
        author_name = csv_author_id_to_name.get(csv_author_id)
        
        if doi is None or author_name is None:
            print(f"Warning: Skipping paper_id={csv_paper_id}, author_id={csv_author_id} - not found in mapping")
            continue
        
        actual_paper_id = doi_to_paper_id.get(doi)
        actual_author_id = name_to_author_id.get(author_name)
        
        if actual_paper_id is None:
            print(f"Warning: Paper with DOI {doi} not found in database")
            continue
        if actual_author_id is None:
            print(f"Warning: Author {author_name} not found in database")
            continue
        
        data.append((actual_paper_id, actual_author_id, author_position))
    
    if data:
        execute_batch(cursor, """
            INSERT INTO paper_authors (paper_id, author_id, author_position)
            VALUES (%s, %s, %s)
            ON CONFLICT (paper_id, author_id) DO NOTHING
        """, data)
        conn.commit()
        print(f"Loaded {len(data)} paper-author relationships")
    else:
        print("No paper-author relationships to load")
    
    cursor.close()

if __name__ == "__main__":
    try:
        load_journals()
        load_journal_metrics()
        load_journal_categories()
        load_papers()
        load_authors()
        load_paper_authors()
        print("All data loaded!")
    finally:
        conn.close()