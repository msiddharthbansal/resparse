import json
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))
with open ('data/processed/category_descriptions.json', 'r') as f:
    category_descriptions = json.load(f)

category_embeddings = {}
for category, desc in category_descriptions.items():
    embedding = model.encode(desc)
    category_embeddings[category] = embedding.tolist()

with open ('data/processed/category_embeddings.json', 'w') as f:
    json.dump(category_embeddings, f)

print (f"Embeddings generated for {len(category_embeddings)} categories!")