# filename: poly186_info.py

import requests
from bs4 import BeautifulSoup
import re

def get_info(query):
    google_search_url = "https://www.google.com/search?q=" + query
    response = requests.get(google_search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='kCrYT')
    urls = []
    for result in search_results:
        if result.a:
            match = re.search('url\?q=(.+?)&sa', str(result.a['href']))
            if match:
                urls.append(match.group(1))
    for url in urls[:5]:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            print(f"\nURL: {url}\n")
            print(" ".join([p.text for p in soup.find_all('p')]))
        except Exception as e:
            print(f"Error while accessing {url}: {e}")

get_info("Poly186")