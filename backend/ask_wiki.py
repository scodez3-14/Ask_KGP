import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()


KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "metakgp-wiki"

pc = Pinecone(api_key=KEY)
index = pc.Index(INDEX_NAME)
model = SentenceTransformer('all-MiniLM-L6-v2')

def ask_question(question, top_n=10):
    query_vector = model.encode(question).tolist()

    results = index.query(
        vector=query_vector,
        top_k=top_n,
        include_metadata=True
    )

    chunks = []
    for match in results['matches']:
        metadata = match.get('metadata', {})
        chunks.append({
            "source": metadata.get('source'),
            "text": metadata.get('text'), 
            "page_id": metadata.get('page'),
            "title": metadata.get('title'),
            "score": match.get('score')
        })
        
    return chunks
