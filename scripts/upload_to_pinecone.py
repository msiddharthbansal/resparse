import os
import json
import psycopg2
from pinecone import Pinecone, ServerlessSpec
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

print("Connecting to Pinecone...")
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
EMBEDDING_DIM = int(os.getenv('EMBEDDING_DIM'))

if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating index '{INDEX_NAME}'...")
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region=os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
        )
    )
    print(f"Index '{INDEX_NAME}' created")
else:
    print(f"Index '{INDEX_NAME}' already exists")

index = pc.Index(INDEX_NAME)

print("Loading embeddings...")
with open('data/processed/paper_embeddings.json', 'r') as f:
    embeddings_data = json.load(f)

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)
cursor = conn.cursor()

print("Uploading to Pinecone...")
vectors_to_upsert = []

for item in tqdm(embeddings_data):
    paper_id = item['paper_id']
    embedding = item['embedding']
    
    cursor.execute("""
        SELECT p.title, p.doi, p.journal_id, p.publication_year, 
               j.journal_name, jm.jif, jm.quartile
        FROM papers p
        JOIN journals j ON p.journal_id = j.journal_id
        LEFT JOIN journal_metrics jm ON j.journal_id = jm.journal_id 
            AND jm.is_current = TRUE
        WHERE p.paper_id = %s
    """, (paper_id,))
    
    row = cursor.fetchone()
    if row:
        title, doi, journal_id, pub_year, journal_name, jif, quartile = row
        
        vectors_to_upsert.append({
            'id': str(paper_id),
            'values': embedding,
            'metadata': {
                'paper_id': paper_id,
                'title': title,
                'doi': doi or '',
                'journal_id': journal_id,
                'journal_name': journal_name,
                'publication_year': pub_year,
                'jif': float(jif) if jif else 0.0,
                'quartile': quartile or 'N/A'
            }
        })
    
    if len(vectors_to_upsert) >= 100:
        index.upsert(vectors=vectors_to_upsert)
        vectors_to_upsert = []

if vectors_to_upsert:
    index.upsert(vectors=vectors_to_upsert)

print(f"Uploaded {len(embeddings_data)} vectors to Pinecone")