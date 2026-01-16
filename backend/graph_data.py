import os
import json
import time
from openai import OpenAI 
from tqdm import tqdm 
from dotenv import load_dotenv

load_dotenv()


MODEL_NAME = "xiaomi/mimo-v2-flash:free" 

# Initialize OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:3000", 
        "X-Title": "Knowledge Graph Builder",    
    }
)

CHUNKS_DIR = "all_soc_chunks"
GRAPH_DIR = "./graph_data"
os.makedirs(GRAPH_DIR, exist_ok=True)

def extract_triplets(chunk_text):
    prompt = f"""
    Extract key relationships from the following text as a JSON list of triplets.
    Each triplet must have: "subject", "predicate", and "object".
    
    TEXT: {chunk_text}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns only valid JSON lists of triplets."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} 
        )
        
        content = response.choices[0].message.content
        if not content:
            return []
            
        data = json.loads(content)
        
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
        return data if isinstance(data, list) else []
        
    except Exception as e:
        print(f"\n[!] Error calling OpenRouter: {e}")
        return []

def process_single_file(filename):
    output_file = os.path.join(GRAPH_DIR, filename)
    input_path = os.path.join(CHUNKS_DIR, filename)
    
    if not os.path.exists(input_path):
        return

    with open(input_path, "r") as f:
        chunks = json.load(f)
    
    print(f"--- Processing {filename} ({len(chunks)} chunks) ---")
    all_triplets = []
    
    for chunk in tqdm(chunks, desc=f"Chunks in {filename}", leave=False):
        text_to_process = f"Context: {chunk.get('title', '')}\nContent: {chunk.get('text', '')}"
        triplets = extract_triplets(text_to_process)
        all_triplets.extend(triplets)
        time.sleep(0.5) 
            
    with open(output_file, "w") as f:
        json.dump(all_triplets, f, indent=2)
    print(f"\n[✓] Saved to {output_file}")

def run_batch_processing():
    files = [f for f in os.listdir(CHUNKS_DIR) if f.endswith(".json")]
    for filename in tqdm(files, desc="Total Files"):
        if os.path.exists(os.path.join(GRAPH_DIR, filename)):
            continue
        process_single_file(filename)

if __name__ == "__main__":
    run_batch_processing()