import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import unquote

BASE = "https://wiki.metakgp.org"
START = "/w/Category:Societies_and_clubs"

def get_all_pages():
    all_pages = []
    next_page = START
    skip_prefixes = []

    while next_page:
        url = urljoin(BASE, next_page)
        print(f"Fetching: {url}")
        
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        links = soup.select("ul.mw-allpages-chunk li a")
        for a in links:
            href = a.get("href")
            if not href: continue
            
            # Skip namespaces
            if any(href.startswith("/w/" + p) for p in skip_prefixes):
                continue
                
            full_url = urljoin(BASE, href)
            all_pages.append(full_url)

        nav_div = soup.select_one("div.mw-allpages-nav")
        next_link = None
        if nav_div:
            links = nav_div.find_all("a")
            for l in links:
                if "Next page" in l.get_text() or (l.get("title") and "Next page" in l.get("title")):
                    next_link = l.get("href")
                    break
        
        next_page = next_link

    return sorted(list(set(all_pages)))
print(f"Total pages found: {len(get_all_pages())}")

