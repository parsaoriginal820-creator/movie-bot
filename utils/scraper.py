import cloudscraper
from bs4 import BeautifulSoup
import re

scraper = cloudscraper.create_scraper()

def search_psarips(query):
    try:
        url = f"https://psarips.eu/?s={query.replace(' ', '+')}"
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        results = []
        for item in soup.select('article'):
            title = item.select_one('h2 a')
            link = title['href'] if title else None
            if link and title:
                results.append({
                    "title": title.text.strip(),
                    "link": link,
                    "source": "PSArips"
                })
        return results[:8]
    except:
        return []

def get_links_from_page(url):
    try:
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = []
        patterns = [
            r'(https?://[^\s\'"]*uptostream\.com/[^\s\'"]*)',
            r'(https?://[^\s\'"]*filemoon\.sx/[^\s\'"]*)',
            r'(https?://[^\s\'"]*streamtape\.com/[^\s\'"]*)',
            r'(https?://[^\s\'"]*dood\.to/[^\s\'"]*)',
        ]
        text = r.text
        for pattern in patterns:
            found = re.findall(pattern, text)
            for link in found:
                if any(q in link.lower() for q in ["1080", "720", "web", "bluray"]):
                    links.append(link)
        return list(set(links))[:6]
    except:
        return []
