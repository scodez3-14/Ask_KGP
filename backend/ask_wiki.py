import chromadb
from sentence_transformers import SentenceTransformer

# 1. Connect to the existing DB and Model
client = chromadb.PersistentClient(path="./metakgp_db")
collection = client.get_collection("wiki_chunks")
model = SentenceTransformer('all-MiniLM-L6-v2')

def ask_question(question, top_n=10):
    query_vector = model.encode(question).tolist()

    # Search the DB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_n
    )

    chunks = []
    # Loop through the results to extract text and all relevant metadata
    for i in range(len(results['documents'][0])):
        metadata = results['metadatas'][0][i]
        chunks.append({
            "source": metadata.get('source'),
            "text": results['documents'][0][i],
            "page_id": metadata.get('page'),
            "title": metadata.get('title')
              # <--- Added this line
        })
    return chunks

