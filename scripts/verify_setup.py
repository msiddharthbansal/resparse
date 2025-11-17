import os
from dotenv import load_dotenv
import psycopg2
import redis
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()

def check_postgres():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            database=os.getenv('POSTGRES_DB')
        )
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT COUNT(*) FROM papers
        """)
        paper_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM journals
        """)
        journal_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"PostgreSQL: {paper_count} papers, {journal_count} journals")
        return True
    except Exception as e:
        print(f"PostgreSQL: {e}")
        return False

def check_redis():
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB'))
        )
        r.ping()
        print("Redis: Connected")
        return True
    except Exception as e:
        print(f"Redis: {e}")
        return False

def check_pinecone():
    try:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
        stats = index.describe_index_stats()
        vector_count = stats['total_vector_count']
        print(f"Pinecone: {vector_count} vectors")
        return True
    except Exception as e:
        print(f"Pinecone: {e}")
        return False

def check_embedding_model():
    try:
        model = SentenceTransformer(os.getenv('EMBEDDING_MODEL'))
        test_embedding = model.encode("test")
        print(f"Embedding Model: Dimension {len(test_embedding)}")
        return True
    except Exception as e:
        print(f"Embedding Model: {e}")
        return False

def check_data_files():
    files_to_check = [
        'data/processed/category_embeddings.json',
        'data/processed/category_descriptions.json'
    ]
    
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"{file}")
        else:
            print(f"{file} not found")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("\nVerifying RESPARSE Setup...\n")
    
    results = {
        "PostgreSQL": check_postgres(),
        "Redis": check_redis(),
        "Pinecone": check_pinecone(),
        "Embedding Model": check_embedding_model(),
        "Data Files": check_data_files()
    }
    
    if all(results.values()):
        print("All systems ready!")
    else:
        print("Some systems need attention")
        for name, status in results.items():
            if not status:
                print(f":: Fix: {name}")
