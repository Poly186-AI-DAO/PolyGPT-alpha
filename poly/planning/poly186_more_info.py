# filename: poly186_more_info.py

from googlesearch import search

def get_urls(query, num_results):
    urls = [url for url in search(query, num_results=num_results)]
    return urls

print("\n".join(get_urls("Poly186", 10)))