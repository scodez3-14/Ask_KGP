import chromadb
from sentence_transformers import SentenceTransformer

# 1. Connect to the existing DB and Model
client = chromadb.PersistentClient(path="./metakgp_db")
collection = client.get_collection("wiki_chunks")
model = SentenceTransformer('all-MiniLM-L6-v2')

def ask_question(question, top_n=10):
    # 2. Turn the question into a vector
    query_vector = model.encode(question).tolist()

    # 3. Search the DB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_n
    )

    # 4. Format and display the results
    print(f"\n--- Results for: {question} ---")
    for i in range(len(results['documents'][0])):
        title = results['metadatas'][0][i]['title']
        page = results['metadatas'][0][i]['page']
        content = results['documents'][0][i]


        print(f"\n[{i+1}] Source: {page} > {title}")
        print("-" * 30)
        print(content + "...") 
        print("-" * 30)

if __name__ == "__main__":
    while True:
        user_query = input("\nAsk MetaKGP (or type 'exit'): ")
        if user_query.lower() == 'exit': break
        ask_question(user_query)