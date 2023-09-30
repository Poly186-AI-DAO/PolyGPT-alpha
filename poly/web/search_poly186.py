# filename: search_poly186.py

import requests
from bs4 import BeautifulSoup

def search_google(query):
    url = "https://www.google.com/search?q=" + query
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    search_results = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
    return search_results[0].get_text()

print(search_google("Poly186"))