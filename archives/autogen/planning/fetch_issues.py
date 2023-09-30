# filename: fetch_issues.py

import requests
import json

def fetch_issues():
    # Replace 'user' and 'repo' with the correct user/organization and repository names
    url = "https://api.github.com/repos/<user>/<repo>/issues"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    params = {'labels': 'good first issue', 'state': 'open'}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        issues = json.loads(response.text)
        for issue in issues:
            print(f"Title: {issue['title']}\nURL: {issue['html_url']}\n")
    else:
        print(f"Failed to fetch issues. Status code: {response.status_code}")

fetch_issues()