from dotenv import load_dotenv
import os

from langchain.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI

load_dotenv('.env')
neo4j_url = os.getenv('NEO4J_URL')
neo4j_username = os.getenv('NEO4J_USERNAME')
neo4j_password = os.getenv('NEO4J_PASSWORD')

def query_knowledge_graph(question: str) -> str:
    """
    Query the knowledge graph using a RAG application with the given question.
    
    Args:
    - question (str): The question to be queried.
    
    Returns:
    - str: The answer or result from the knowledge graph.
    """
    
    # Initialize the Neo4jGraph object
    neo4j_graph = Neo4jGraph(url=neo4j_url, username=neo4j_username, password=neo4j_password)
    
    # Refresh the graph schema
    neo4j_graph.refresh_schema()
    
    # Create the GraphCypherQAChain for querying
    cypher_chain = GraphCypherQAChain.from_llm(
        graph=neo4j_graph,
        cypher_llm=ChatOpenAI(temperature=0, model="gpt-4"),
        qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        validate_cypher=True,  # Validate relationship directions
        verbose=True
    )
    
    return cypher_chain.run(question)

# Example usage:
# result = query_knowledge_graph("When was Walter Elias Disney born?")
# print(result)
