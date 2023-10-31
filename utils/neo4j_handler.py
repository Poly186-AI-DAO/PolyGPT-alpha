import os

from langchain.graphs import Neo4jGraph
from dotenv import load_dotenv

# from chains import (
#     load_embedding_model,
# )

from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate

# from chains import (
#     load_embedding_model,
# )

load_dotenv("../.env")

# Retrieving environment variables
url = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
embedding_model_name = os.getenv("EMBEDDING_MODEL")
llm_name = os.getenv("LLM")

# Check if the environment variables have been retrieved
if not url:
    raise ValueError("NEO4J_URI not found in environment variables!")
if not username:
    raise ValueError("NEO4J_USERNAME not found in environment variables!")
if not password:
    raise ValueError("NEO4J_PASSWORD not found in environment variables!")
if not embedding_model_name:
    raise ValueError("EMBEDDING_MODEL not found in environment variables!")
if not llm_name:
    raise ValueError("LLM not found in environment variables!")

# Remapping for Langchain Neo4j integration
os.environ["NEO4J_URL"] = url


# embeddings, dimension = load_embedding_model(
#     embedding_model_name,
#     "openai",
#     logger=BaseLogger(),
# )

# if Neo4j is local, you can go to http://localhost:7474/ to browse the database
neo4j_graph = Neo4jGraph(url=url, username=username, password=password)
# create_vector_index(neo4j_graph, dimension)

# llm = load_llm(
#     llm_name, logger=BaseLogger(), config={"ollama_base_url": ollama_base_url}
# )

# llm_chain = configure_llm_only_chain(llm)
# rag_chain = configure_qa_rag_chain(
#     llm, embeddings, embeddings_store_url=url, username=username, password=password
# )


# Seed the database
neo4j_graph.query(
    """
MERGE (m:Movie {name:"Top Gun"})
WITH m
UNWIND ["Tom Cruise", "Val Kilmer", "Anthony Edwards", "Meg Ryan"] AS actor
MERGE (a:Actor {name:actor})
MERGE (a)-[:ACTED_IN]->(m)
"""
)

# Refresh the graph schema information
neo4j_graph.refresh_schema()
print(neo4j_graph.schema)

# Query the graph
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=neo4j_graph, verbose=True
)
print(chain.run("Who played in Top Gun?"))

# Limit the number of results
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=neo4j_graph, verbose=True, top_k=2
)
print(chain.run("Who played in Top Gun?"))

# Return intermediate results
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=neo4j_graph, verbose=True, return_intermediate_steps=True
)
result = chain("Who played in Top Gun?")
print(f"Intermediate steps: {result['intermediate_steps']}")
print(f"Final answer: {result['result']}")

# Return direct results
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=neo4j_graph, verbose=True, return_direct=True
)
print(chain.run("Who played in Top Gun?"))

# Add examples in the Cypher generation prompt
CYPHER_GENERATION_TEMPLATE = """... (the template here) ..."""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)
chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0),
    graph=neo4j_graph,
    verbose=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT,
)
print(chain.run("How many people played in Top Gun?"))

# Use separate LLMs for Cypher and answer generation
chain = GraphCypherQAChain.from_llm(
    graph=neo4j_graph,
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
    verbose=True,
)
print(chain.run("Who played in Top Gun?"))

# Ignore specified node and relationship types
chain = GraphCypherQAChain.from_llm(
    graph=neo4j_graph,
    cypher_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
    verbose=True,
    exclude_types=["Movie"],
)
print(chain.graph_schema)

# Validate generated Cypher statements
chain = GraphCypherQAChain.from_llm(
    llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
    graph=neo4j_graph,
    verbose=True,
    validate_cypher=True,
)
print(chain.run("Who played in Top Gun?"))
