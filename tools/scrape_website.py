from dotenv import load_dotenv
import json
import os
import requests
from bs4 import BeautifulSoup

from tools.summary import summary
from langchain.document_loaders import BrowserlessLoader
from langchain.vectorstores import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv('.env')
browserless_api_key = os.getenv('BROWSERLESS_API_KEY')
neo4j_url = os.getenv('NEO4J_URL')
neo4j_username = os.getenv('NEO4J_USERNAME')
neo4j_password = os.getenv('NEO4J_PASSWORD')

def scrape_website(url, objective):
    # The agent would access the given URL and extract the necessary data.
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
    response = requests.post(post_url, headers=headers, data=data_json, timeout=10)
    
    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()

        # Summarize the text if it's too long
        output = summary(objective, text) if len(text) > 10000 else text

        # Load the summarized text as documents
        loader = BrowserlessLoader(
            api_token=browserless_api_key,
            urls=[url],
            text_content=True,
        )
        documents = loader.load(text=output)  # Use the summarized output

        # Create a Neo4j vector store from the documents
        embeddings = OpenAIEmbeddings()
        db = Neo4jVector.from_documents(
            documents, embeddings, url=neo4j_url, username=neo4j_username, password=neo4j_password
        )

        # Perform a similarity search with the summarized text
        matched_documents = []
        docs_with_score = db.similarity_search_with_score(output, k=2)
        for doc, score in docs_with_score:
            matched_documents.append({
                "score": score,
                "content": doc.page_content
            })

        return {
            "summary": output,
            "matched_documents": matched_documents
        }

    else:
        print(f"HTTP request failed with status code {response.status_code}")
        return None
