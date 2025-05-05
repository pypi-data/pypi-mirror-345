import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque


def normalize_url(url):
    """Normalize URL by removing trailing slashes and converting to lowercase."""
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    return f"{parsed.scheme}://{parsed.netloc}{path}".lower()


def get_all_links(base_url, max_links=4):
    visited = set()
    to_visit = deque([base_url])
    normalized_base = normalize_url(base_url)

    while to_visit and len(visited) < max_links:
        url = to_visit.popleft()
        normalized_url = normalize_url(url)

        if normalized_url in visited:
            continue

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            visited.add(normalized_url)

            for link in soup.find_all('a', href=True):
                absolute_link = urljoin(base_url, link['href'])
                normalized_link = normalize_url(absolute_link)

                if normalized_link.startswith(normalized_base) and normalized_link not in visited:
                    to_visit.append(absolute_link)

                    if len(visited) >= max_links:
                        return visited

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url}: {e}")

    return visited
