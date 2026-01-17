from bs4 import BeautifulSoup, Comment
import re
import uuid
from scraper import fetch_page

def get_clean_text(element):
    """Extracts text and cleans up wiki-specific artifacts like [1] or [edit]."""
    if not element: return ""
    text = element.get_text(" ", strip=True)
    text = re.sub(r'\[\d+\]|\[edit\]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

def format_node(elem):
    """Converts specific HTML nodes into readable text formats."""
    if elem.name == 'table':
        rows = []
        for tr in elem.find_all('tr'):
            cells = [get_clean_text(td) for td in tr.find_all(['td', 'th']) if td.get_text().strip()]
            if cells: rows.append(" | ".join(cells))
        return "\n".join(rows)
    
    if elem.name in ['ul', 'ol']:
        items = [f"• {get_clean_text(li)}" for li in elem.find_all('li', recursive=False)]
        return "\n".join(items)
    
    return get_clean_text(elem)

def chunk_metakgp_html(html, page_name):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="mw-parser-output") or soup.find("div", id="mw-content-text") or soup

    chunks = []
    
    infobox = content.find("table", class_="infobox")
    if infobox:
        chunks.append({
            "chunk_id": f"info_{uuid.uuid4().hex[:6]}",
            "title": f"{page_name} - Quick Facts",
            "text": format_node(infobox),
            "page": page_name
        })
        infobox.decompose()

    current_title = page_name 
    current_buffer = []

    for elem in content.find_all(recursive=False):
        is_header = elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'] or 'mw-heading' in elem.get('class', [])
        
        if is_header:
            if current_buffer:
                chunks.append({
                    "chunk_id": uuid.uuid4().hex[:8],
                    "title": current_title,
                    "text": "\n".join(current_buffer),
                    "page": page_name
                })
                current_buffer = []
            
            header_tag = elem if elem.name in ['h1', 'h2', 'h3'] else elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            current_title = get_clean_text(header_tag) if header_tag else "Section"
        else:
            text = format_node(elem)
            if text and len(text) > 5:
                current_buffer.append(text)

    if current_buffer:
     chunks.append({
        "chunk_id": uuid.uuid4().hex[:8],
        "title": current_title,
        "text": "\n".join(current_buffer),
        "page": page_name,  # Added missing comma here
        "source": f"https://wiki.metakgp.org/w/{page_name}"  # Fixed URL construction
    })

    return chunks

