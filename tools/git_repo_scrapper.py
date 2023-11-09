import os
import logging
import queue
import json
from git import Repo
from langchain.document_loaders import GitLoader
from utils.neo4j_wrapper import KnowledgeGraphQuery

from utils.poly_logger import PolyLogger
from langchain.docstore.document import Document


CHAT = 25  # Custom logging level
logging.addLevelName(CHAT, "CHAT")
JSON_LOGGING = False  # Assuming a default value; adjust as necessary



def git_repo_scraper(repo_url, branch='main', repo_path='./repo', file_filter=None):
    logger = PolyLogger(__name__)

    logger.info(f"Cloning repository: {repo_url} with branch: {branch}")
    repo = Repo.clone_from(repo_url, to_path=repo_path, branch=branch)
    logger.info(f"Cloning repository: {repo_url} with branch: {branch}")
    logger.info(f"Loading files from repository: {repo_url}")
    loader = GitLoader(repo_path=repo_path, file_filter=file_filter)
    data = loader.load()

    logger.info(f"Saving {len(data)} files to Neo4j database")
    documents = [Document(file_name=d['file_name'], text=d['page_content']) for d in data]
    kg_query = KnowledgeGraphQuery()
    store = kg_query.create_vector_store_from_docs(documents)
    kg_query.add_documents_to_store(store, documents)

    logger.info(f"Deleting cloned repository folder: {repo_path}")
    os.rmdir(repo_path)

    logger.info(f"Process completed successfully for repository: {repo_url}")
    return documents


# Sample usage:
# documents = git_repo_scraper(
#     repo_url="https://github.com/langchain-ai/langchain",
#     branch='main',
#     file_filter=lambda file_path: file_path.endswith(".py"),
# )
