# filename: web_scrape.py

import requests
from bs4 import BeautifulSoup

url = "https://www.example.com"  # replace with your URL

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

paragraphs = soup.find_all('p')

for p in paragraphs:
    print(p.get_text())