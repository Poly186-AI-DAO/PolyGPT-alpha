import os
from dotenv import load_dotenv
from langchain.callbacks.base import BaseCallbackHandler
from langchain.graphs import Neo4jGraph
from utils import create_vector_index
from chains import (
    load_embedding_model,
    load_llm,
    configure_llm_only_chain,
    configure_qa_rag_chain,
    generate_ticket,
)

class ChatAssistant:
    def __init__(self):
        # Load environment variables
        load_dotenv(".env")
        self.url = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL")
        self.llm_name = os.getenv("LLM")
        
        # Initialize Neo4jGraph
        self.neo4j_graph = Neo4jGraph(url=self.url, username=self.username, password=self.password)
        
        # Load embedding model and create vector index
        self.embeddings, self.dimension = load_embedding_model(
            self.embedding_model_name, config={"ollama_base_url": self.ollama_base_url}
        )
        create_vector_index(self.neo4j_graph, self.dimension)
        
        # Load LLM and configure chains
        self.llm = load_llm(self.llm_name, config={"ollama_base_url": self.ollama_base_url})
        self.llm_chain = configure_llm_only_chain(self.llm)
        self.rag_chain = configure_qa_rag_chain(
            self.llm, self.embeddings, embeddings_store_url=self.url, 
            username=self.username, password=self.password
        )

    class StreamHandler(BaseCallbackHandler):
        def __init__(self, initial_text=""):
            self.text = initial_text

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            self.text += token

    def chat_input(self, input_text: str, mode: str):
        if mode == "LLM only" or mode == "Disabled":
            output_function = self.llm_chain
        elif mode == "Vector + Graph" or mode == "Enabled":
            output_function = self.rag_chain

        result = output_function({"question": input_text, "chat_history": []})
        return result["answer"]

    def generate_ticket_draft(self, input_question: str):
        new_title, new_question = generate_ticket(
            neo4j_graph=self.neo4j_graph,
            llm_chain=self.llm_chain,
            input_question=input_question
        )
        return new_title, new_question


# assistant = ChatAssistant()
# response = assistant.chat_input("What is Python?", "Enabled")
# print(response)

# ticket_title, ticket_description = assistant.generate_ticket_draft("What is Python?")
# print(ticket_title, ticket_description)
