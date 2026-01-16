import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./metakgp_db")
collection = client.get_or_create_collection("wiki_chunks")
model = SentenceTransformer('all-MiniLM-L6-v2')

def run_db_filler():
    chunk_files = [f for f in os.listdir("./all_soc_chunks") if f.endswith(".json")]
    
    for filename in chunk_files:
        with open(f"./all_soc_chunks/{filename}", "r") as f:
            chunks = json.load(f)
        
        if not chunks: continue
            
        texts = [c['text'] for c in chunks]
        embeddings = model.encode(texts).tolist()
        collection.add(
            ids=[f"{c['page']}_{c['chunk_id']}" for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"title": c['title'], "page": c['page']} for c in chunks]
        )
        print(f"Indexed into DB: {filename}")

if __name__ == "__main__":
    run_db_filler()