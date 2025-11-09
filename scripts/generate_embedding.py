import os
import psycopg2
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv
import json

load_dotenv()

print("Loading embedding model...")
model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)
cursor = conn.cursor()

cursor.execute("""
    SELECT paper_id, abstract FROM papers 
    WHERE abstract IS NOT NULL AND abstract != ''
    ORDER BY paper_id
""")
papers = cursor.fetchall()

print(f"Generating embeddings for {len(papers)} papers...")

embeddings_data = []

BATCH_SIZE = 32
for i in tqdm(range(0, len(papers), BATCH_SIZE)):
    batch = papers[i:i+BATCH_SIZE]
    paper_ids = [p[0] for p in batch]
    abstracts = [p[1] for p in batch]
    
    embeddings = model.encode(abstracts, show_progress_bar=False)
    
    for paper_id, embedding in zip(paper_ids, embeddings):
        embeddings_data.append({
            'paper_id': int(paper_id),
            'embedding': embedding.tolist()
        })

with open('data/processed/paper_embeddings.json', 'w') as f:
    json.dump(embeddings_data, f)

print(f"Generated {len(embeddings_data)} embeddings!")

cursor.close()
conn.close()