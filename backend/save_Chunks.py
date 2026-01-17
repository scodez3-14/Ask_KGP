import json
import os
from scraper import fetch_page   
from GetChunks import chunk_metakgp_html
from crawl_soc import get_soc_links

CHUNK_DIR = "./all_soc_chunks"
os.makedirs(CHUNK_DIR, exist_ok=True)

def run_harvester():
    all_urls =get_soc_links()
    for url in all_urls:
        page_id = url.split("/")[-1]
        file_path = os.path.join(CHUNK_DIR, f"{page_id}.json")
        
        if os.path.exists(file_path): continue
            
        html = fetch_page(url)
        if html:
            chunks = chunk_metakgp_html(html, page_id.replace("_", " "))
            with open(file_path, "w") as f:
                json.dump(chunks, f)
            print(f"Saved JSON: {page_id}")

if __name__ == "__main__":
    run_harvester()