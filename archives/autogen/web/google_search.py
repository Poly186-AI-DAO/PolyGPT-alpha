# filename: google_search.py

from googleapiclient.discovery import build

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']

def main():
    # replace with your own API key and CSE ID
    api_key = "YOUR_API_KEY"
    cse_id = "YOUR_CSE_ID"
    
    results = google_search("langchain library", api_key, cse_id, num=10)
    for result in results:
        print("Title:", result['title'])
        print("Snippet:", result['snippet'])
        print("Link:", result['link'])
        print("---------------------------------------------------------")

if __name__ == "__main__":
    main()