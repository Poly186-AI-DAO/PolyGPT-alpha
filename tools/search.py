import requests
from bs4 import BeautifulSoup


def search(query):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    url = 'https://www.google.com/search?gl=us&q=' + requests.utils.quote(query)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all the search result this div wrapper
    result_divs = soup.find_all('div', class_='Gx5Zad fP1Qef xpd EtOod pkphOe')
    results = []

    for div in result_divs:
        # Only get the organic_results
        if div.find('div', class_='egMi0 kCrYT') is None:
            continue

        # Extracting the title (linked text) from h3
        title = div.find('h3').text
        # Extracting the URL
        link = div.find('a')['href']
        # Extracting the brief description
        description = div.find('div', class_='BNeawe s3v9rd AP7Wnd').text

        results.append({'title': title, 'link': link, 'description': description})
    
    return results
