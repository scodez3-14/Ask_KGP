import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent                     


# 1. Initialize DB and Model
client = chromadb.PersistentClient(path=BASE_DIR/"metakgp_db")
# Add this right after you initialize the client
try:
    client.delete_collection("wiki_chunks")
    print("🧹 Deleted old collection to ensure fresh metadata.")
except Exception:
    pass

collection = client.get_or_create_collection("wiki_chunks")
model = SentenceTransformer('all-MiniLM-L6-v2')

def run_db_filler():
    source_folder = ROOT_DIR/"all_soc_chunks"
    chunk_files = [f for f in os.listdir(source_folder) if f.endswith(".json")]
    
    total_indexed = 0
    
    for filename in chunk_files:
        with open(os.path.join(source_folder, filename), "r") as f:
            chunks = json.load(f)
        
        if not chunks:
            continue

        # Prepare lists for batch processing this file
        texts = []
        ids = []
        metadatas = []

        for c in chunks:
            # We use the text to create embeddings
            texts.append(c['text'])
            
            # Use the chunk_id from your JSON as the unique DB ID
            ids.append(c['chunk_id'])
            
            # Store everything else in metadata for the UI to use
            metadatas.append({
                "title": c.get('title', 'Unknown'),
                "page": c.get('page', 'Unknown'),
                "source": c.get('source', 'https://wiki.metakgp.org')
            })

        # Generate embeddings for the whole file at once
        embeddings = model.encode(texts).tolist()

        # Use upsert so you can rerun the script without duplicate errors
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        total_indexed += len(texts)
        print(f"✅ Indexed {len(texts)} chunks from: {filename}")

    print(f"\n✨ Success! Total chunks in DB: {collection.count()}")

if __name__ == "__main__":
    run_db_filler()