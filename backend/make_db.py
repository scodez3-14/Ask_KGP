import os
import json
from pathlib import Path
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

# 1. Setup Directions
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "metakgp-wiki"

pc = Pinecone(api_key=KEY)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create index if it doesn't exist
# all-MiniLM-L6-v2 produces vectors of size 384
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384, 
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1') # Adjust region as needed
    )

index = pc.Index(INDEX_NAME)

def run_db_filler():
    source_folder = ROOT_DIR/"all_soc_chunks"
    chunk_files = [f for f in os.listdir(source_folder) if f.endswith(".json")]
    
    total_indexed = 0
    
    for filename in chunk_files:
        with open(source_folder / filename, "r") as f:
            chunks = json.load(f)
        
        if not chunks:
            continue

        # Prepare data for Pinecone
        texts = [c['text'] for c in chunks]
        embeddings = model.encode(texts).tolist()
        
        vectors_to_upsert = []
        for i, c in enumerate(chunks):
            vectors_to_upsert.append({
                "id": c['chunk_id'],
                "values": embeddings[i],
                "metadata": {
                    "text": c['text'], # Pinecone doesn't store 'documents' separately; we put it in metadata
                    "title": c.get('title', 'Unknown'),
                    "page": c.get('page', 'Unknown'),
                    "source": c.get('source', 'https://wiki.metakgp.org')
                }
            })

        # Pinecone upsert (standard limit is 100-1000 per batch)
        index.upsert(vectors=vectors_to_upsert)
        
        total_indexed += len(texts)
        print(f"✅ Indexed {len(texts)} chunks from: {filename}")

    stats = index.describe_index_stats()
    print(f"\n✨ Success! Total vectors in Pinecone: {stats['total_vector_count']}")

if __name__ == "__main__":
    run_db_filler()