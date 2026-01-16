import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://wiki.metakgp.org"
START = "/w/Category:Societies_and_clubs"

def get_soc_links():
    all_pages = []
    next_page = START

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

        pages_div = soup.find("div", id="mw-pages")
        if pages_div:
            links = pages_div.find_all("a")
            for a in links:
                href = a.get("href")
                if href and "/w/" in href and "pagefrom" not in href:
                    full_url = urljoin(BASE, href)
                    all_pages.append(full_url)

        next_page = None
        if pages_div:
            nav_links = pages_div.find_all("a")
            for link in nav_links:
                if "next page" in link.get_text().lower():
                    next_page = link.get("href")
                    break

    return sorted(list(set(all_pages)))

pages = get_soc_links()
for p in pages:
    print(p)

print(f"\nTotal societies/pages found: {len(pages)}")