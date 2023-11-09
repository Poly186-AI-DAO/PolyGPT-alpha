import os
from langchain.graphs import Neo4jGraph
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Neo4jVector
from langchain.document_loaders import TextLoader
from langchain.docstore.document import Document

from utils.chains import load_embedding_model, load_llm
from utils.poly_logger import PolyLogger

class KnowledgeGraphQuery:
    """
    A class to handle queries on a knowledge graph using the GraphCypherQAChain.
    """

    def __init__(self):
        """
        Initializes the KnowledgeGraphQuery by setting up the environment, loading necessary models, and establishing a connection to the Neo4j graph.
        """
        # Load environment variables from the .env file
        load_dotenv("../.env")
        
        # Retrieve necessary environment variables
        self.url = os.getenv("NEO4J_URI")
        self.username = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL")
        self.llm_name = os.getenv("LLM")

        # Remap URL for Langchain Neo4j integration
        os.environ["NEO4J_URL"] = self.url

        # Load embedding model and get its dimension
        self.embeddings, self.dimension = load_embedding_model(
            self.embedding_model_name,
            config="openai",
            logger=PolyLogger(__name__),
        )
        
        # Establish a connection to the Neo4j graph
        self.neo4j_graph = Neo4jGraph(url=self.url, username=self.username, password=self.password)
        self.neo4j_graph.refresh_schema()
        
        # Create a vector index for the graph
        self.create_vector_index(self.neo4j_graph, self.dimension)

        # Load the language model
        self.llm = load_llm(self.llm_name, logger=PolyLogger(__name__), config="openai")

    def run_direct_query(self, question: str) -> str:
        """
        Runs a direct query on the knowledge graph.
        
        Args:
        - question (str): The question to be queried.

        Returns:
        - str: The answer or result from the knowledge graph.
        """
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0), graph=self.neo4j_graph, verbose=True, return_direct=True
        )
        return chain.run(question)
    
    def add_cypher_prompt(self, question: str, cypher_generation_prompt: PromptTemplate) -> str:
        """
        Runs a query using a custom Cypher generation prompt.
        
        Args:
        - question (str): The question to be queried.
        - cypher_generation_prompt (PromptTemplate): The custom Cypher generation prompt.

        Returns:
        - str: The answer or result from the knowledge graph.
        """
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(temperature=0),
            graph=self.neo4j_graph,
            verbose=True,
            cypher_prompt=cypher_generation_prompt,
        )
        return chain.run(question)
    
    def use_separate_llms(self, question: str) -> str:
        """
        Runs a query using separate LLMs for Cypher and answer generation.
        
        Args:
        - question (str): The question to be queried.

        Returns:
        - str: The answer or result from the knowledge graph.
        """
        chain = GraphCypherQAChain.from_llm(
            graph=self.neo4j_graph,
            cypher_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
            qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
            verbose=True,
        )
        return chain.run(question)
    
    def ignore_specified_types(self, question: str, types_to_exclude: list) -> str:
        """
        Runs a query while ignoring specified node and relationship types.
        
        Args:
        - question (str): The question to be queried.
        - types_to_exclude (list): List of types to be excluded.

        Returns:
        - str: The updated graph schema after excluding the specified types.
        """
        chain = GraphCypherQAChain.from_llm(
            graph=self.neo4j_graph,
            cypher_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
            qa_llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k"),
            verbose=True,
            exclude_types=types_to_exclude,
        )
        return chain.graph_schema
    
    def validate_cypher(self, question: str) -> str:
        """
        Runs a query and validates the generated Cypher statements.
        
        Args:
        - question (str): The question to be queried.

        Returns:
        - str: The answer or result from the knowledge graph after validating the Cypher.
        """
        chain = GraphCypherQAChain.from_llm(
            llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo"),
            graph=self.neo4j_graph,
            verbose=True,
            validate_cypher=True,
        )
        return chain.run(question)


    def create_vector_store_from_docs(self, docs, index_name="vector"):
        """
        Creates a vector store in Neo4j from documents.

        Args:
            docs: List of documents to be added to the vector store.
            index_name (str): The name of the index to be created.

        Returns:
            A Neo4jVector instance.
        """
        return Neo4jVector.from_documents(
            docs, OpenAIEmbeddings(), url=self.url, username=self.username, password=self.password, index_name=index_name
        )

    def create_vector_store_from_existing_index(self, index_name="vector"):
        """
        Initializes a vector store from an existing Neo4j index.

        Args:
            index_name (str): The name of the existing index.

        Returns:
            A Neo4jVector instance.
        """
        return Neo4jVector.from_existing_index(
            OpenAIEmbeddings(),
            url=self.url,
            username=self.username,
            password=self.password,
            index_name=index_name,
        )

    def add_documents_to_store(self, store, documents):
        """
        Adds documents to the existing vector store.

        Args:
            store: The Neo4jVector instance.
            documents: List of documents to be added to the store.

        Returns:
            A list of document IDs.
        """
        return store.add_documents(documents)

    def hybrid_search_setup(self, docs, index_name="vector", keyword_index_name="keyword"):
        """
        Sets up the hybrid search with both vector and keyword indices.

        Args:
            docs: List of documents to be added to the vector store.
            index_name (str): The name of the vector index.
            keyword_index_name (str): The name of the keyword index.

        Returns:
            A Neo4jVector instance.
        """
        return Neo4jVector.from_documents(
            docs,
            OpenAIEmbeddings(),
            url=self.url,
            username=self.username,
            password=self.password,
            index_name=index_name,
            keyword_index_name=keyword_index_name,
            search_type="hybrid",
        )

    def setup_retriever(self, store):
        """
        Sets up a retriever for the Neo4jVector.

        Args:
            store: The Neo4jVector instance.

        Returns:
            A retriever instance.
        """
        return store.as_retriever()

    def qa_with_sources(self, retriever, question):
        """
        Conducts question-answering with sources using the RetrievalQAWithSourcesChain.

        Args:
            retriever: The retriever instance.
            question (str): The question to be answered.

        Returns:
            A dictionary with the answer and sources.
        """
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0), chain_type="stuff", retriever=retriever
        )
        return chain({"question": question}, return_only_outputs=True)

    def create_vector_index(driver, dimension: int) -> None:
        index_query = "CALL db.index.vector.createNodeIndex('stackoverflow', 'Question', 'embedding', $dimension, 'cosine')"
        try:
            driver.query(index_query, {"dimension": dimension})
        except:  # Already exists
            pass
        index_query = "CALL db.index.vector.createNodeIndex('top_answers', 'Answer', 'embedding', $dimension, 'cosine')"
        try:
            driver.query(index_query, {"dimension": dimension})
        except:  # Already exists
            pass


    def create_constraints(driver):
        driver.query(
            "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:Question) REQUIRE (q.id) IS UNIQUE"
        )
        driver.query(
            "CREATE CONSTRAINT answer_id IF NOT EXISTS FOR (a:Answer) REQUIRE (a.id) IS UNIQUE"
        )
        driver.query(
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE (u.id) IS UNIQUE"
        )
        driver.query(
            "CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE (t.name) IS UNIQUE"
        )


