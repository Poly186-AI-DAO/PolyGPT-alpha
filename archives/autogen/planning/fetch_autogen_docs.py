# filename: fetch_autogen_docs.py

import requests
from bs4 import BeautifulSoup

def fetch_autogen_docs():
    url = "https://microsoft.github.io/autogen/docs/Getting-Started"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.prettify().encode('utf-8'))
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")

fetch_autogen_docs()