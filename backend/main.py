import os
from fastapi import FastAPI
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# --- CONFIGURATION ---
client = chromadb.PersistentClient(path="./metakgp_db")
collection = client.get_collection("wiki_chunks")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Replace with your actual Gemini API Key
ai_cli=genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class UserQuery(BaseModel):
    text: str


def get_rag_response(question):
    # 1. Get Chunks (Your existing logic)
    query_vector = model.encode(question).tolist()
    results = collection.query(query_embeddings=[query_vector], n_results=5)
    
    context = "\n\n".join(results['documents'][0])
    sources = list(set([m['page'] for m in results['metadatas'][0]]))

    # 2. Feed to AI
    prompt = f"""
    You are the MetaKGP Wiki Assistant. Using the context provided, answer the user's question.
    If the context doesn't contain the answer, say "I don't have enough information in the wiki if u cant find answer and return the chunks."
    
    CONTEXT:
    {context}
    
    QUESTION: {question}
    """
    
    response = ai_cli.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text, sources

@app.post("/ask")
async def ask_endpoint(query: UserQuery):
    answer, sources = get_rag_response(query.text)
    return {"answer": answer, "sources": sources}