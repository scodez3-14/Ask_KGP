import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "MetaKGP-Research-Bot (contact: your-email@example.com)"
}

def fetch_page(url):
    """
    Fetches a MetaKGP wiki page and returns cleaned HTML content.
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        content_element = soup.find("div", id="mw-content-text")

        if content_element:
            for extra in content_element.find_all(
                ["div", "table"],
                class_=["printfooter", "mw-editsection"]
            ):
                extra.decompose()

            return str(content_element)

        return ""

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

def main():
    target_url = "https://wiki.metakgp.org/w/AGV"
    print(f"Scraping: {target_url}...")

    html = fetch_page(target_url)

    if html:
        print("HTML successfully fetched.")
        return html
    else:
        print("Crawl failed.")
        return None

if __name__ == "__main__":
    html = main()


