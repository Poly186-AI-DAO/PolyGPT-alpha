from langchain.chains import GraphCypherQAChain

def query_knowledge_graph(question: str) -> str:
    """
    Query the knowledge graph using a RAG application with the given question.
    
    Args:
    - question (str): The question to be queried.
    
    Returns:
    - str: The answer or result from the knowledge graph.
    """
    
    # Assuming that the graph object is already available in the current scope.
    graph.refresh_schema()
    
    cypher_chain = GraphCypherQAChain.from_llm(
        graph=graph,
        cypher_llm=ChatOpenAI(temperature=0, model="gpt-4"),
        qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
        validate_cypher=True,  # Validate relationship directions
        verbose=True
    )
    
    return cypher_chain.run(question)

# Example usage:
# result = query_knowledge_graph("When was Walter Elias Disney born?")
# print(result)
