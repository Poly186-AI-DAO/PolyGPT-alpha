import os
from dotenv import load_dotenv
from langchain.graphs import Neo4jGraph
from chains import load_embedding_model
from utils import create_constraints, create_vector_index
import requests

load_dotenv(".env")

class StackOverflowLoader:
    def __init__(self):
        url = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        embedding_model_name = os.getenv("EMBEDDING_MODEL")
        # Remapping for Langchain Neo4j integration
        os.environ["NEO4J_URL"] = url

        self.so_api_base_url = "https://api.stackexchange.com/2.3/search/advanced"

        self.embeddings, self.dimension = load_embedding_model(
            embedding_model_name, config={"ollama_base_url": ollama_base_url}
        )

        # if Neo4j is local, you can go to http://localhost:7474/ to browse the database
        self.neo4j_graph = Neo4jGraph(url=url, username=username, password=password)

        create_constraints(self.neo4j_graph)
        create_vector_index(self.neo4j_graph, self.dimension)

    def load_so_data(self, tag="neo4j", page=1):
        parameters = (
            f"?pagesize=100&page={page}&order=desc&sort=creation&answers=1&tagged={tag}"
            "&site=stackoverflow&filter=!*236eb_eL9rai)MOSNZ-6D3Q6ZKb0buI*IVotWaTb"
        )
        data = requests.get(self.so_api_base_url + parameters).json()
        self.insert_so_data(data)

    def load_high_score_so_data(self):
        parameters = (
            f"?fromdate=1664150400&order=desc&sort=votes&site=stackoverflow&"
            "filter=!.DK56VBPooplF.)bWW5iOX32Fh1lcCkw1b_Y6Zkb7YD8.ZMhrR5.FRRsR6Z1uK8*Z5wPaONvyII"
        )
        data = requests.get(self.so_api_base_url + parameters).json()
        self.insert_so_data(data)

    def insert_so_data(self, data):
        # Calculate embedding values for questions and answers
        for q in data["items"]:
            question_text = q["title"] + "\n" + q["body_markdown"]
            q["embedding"] = self.embeddings.embed_query(question_text)
            for a in q.get("answers", []):
                a["embedding"] = self.embeddings.embed_query(
                    question_text + "\n" + a["body_markdown"]
                )

        # Cypher, the query language of Neo4j, is used to import the data
        import_query = """
        UNWIND $data AS q
        MERGE (question:Question {id:q.question_id}) 
        ON CREATE SET question.title = q.title, question.link = q.link, question.score = q.score,
            question.favorite_count = q.favorite_count, question.creation_date = datetime({epochSeconds: q.creation_date}),
            question.body = q.body_markdown, question.embedding = q.embedding
        FOREACH (tagName IN q.tags | 
            MERGE (tag:Tag {name:tagName}) 
            MERGE (question)-[:TAGGED]->(tag)
        )
        FOREACH (a IN q.answers |
            MERGE (question)<-[:ANSWERS]-(answer:Answer {id:a.answer_id})
            SET answer.is_accepted = a.is_accepted,
                answer.score = a.score,
                answer.creation_date = datetime({epochSeconds:a.creation_date}),
                answer.body = a.body_markdown,
                answer.embedding = a.embedding
            MERGE (answerer:User {id:coalesce(a.owner.user_id, "deleted")}) 
            ON CREATE SET answerer.display_name = a.owner.display_name,
                        answerer.reputation= a.owner.reputation
            MERGE (answer)<-[:PROVIDED]-(answerer)
        )
        WITH * WHERE NOT q.owner.user_id IS NULL
        MERGE (owner:User {id:q.owner.user_id})
        ON CREATE SET owner.display_name = q.owner.display_name,
                    owner.reputation = q.owner.reputation
        MERGE (owner)-[:ASKED]->(question)
        """
        self.neo4j_graph.query(import_query, {"data": data["items"]})
