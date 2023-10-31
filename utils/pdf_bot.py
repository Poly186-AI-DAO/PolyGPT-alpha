import os
from PyPDF2 import PdfReader
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.neo4j_vector import Neo4jVector
from chains import (
    load_embedding_model,
    load_llm,
)

# load api key lib
from dotenv import load_dotenv

load_dotenv(".env")

url = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")
ollama_base_url = os.getenv("OLLAMA_BASE_URL")
embedding_model_name = os.getenv("EMBEDDING_MODEL")
llm_name = os.getenv("LLM")
# Remapping for Langchain Neo4j integration
os.environ["NEO4J_URL"] = url

embeddings, dimension = load_embedding_model(
    embedding_model_name, config={"ollama_base_url": ollama_base_url}, logger=None
)

llm = load_llm(llm_name, logger=None, config={"ollama_base_url": ollama_base_url})


class PDFChatBot:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.text = self.extract_text_from_pdf()
        self.chunks = self.split_text_into_chunks()
        self.vectorstore = self.store_chunks_in_db()
        self.qa = self.create_qa_chain()

    def extract_text_from_pdf(self):
        pdf_reader = PdfReader(self.pdf_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def split_text_into_chunks(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, length_function=len
        )
        chunks = text_splitter.split_text(text=self.text)
        return chunks

    def store_chunks_in_db(self):
        vectorstore = Neo4jVector.from_texts(
            self.chunks,
            url=url,
            username=username,
            password=password,
            embedding=embeddings,
            index_name="pdf_bot",
            node_label="PdfBotChunk",
            pre_delete_collection=True,  # Delete existing PDF data
        )
        return vectorstore

    def create_qa_chain(self):
        qa = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=self.vectorstore.as_retriever()
        )
        return qa

    def ask_question(self, query):
        response = self.qa.run(query)
        return response


def main():
    pdf_path = "path/to/your/pdf/file.pdf"  # replace this with the path to your PDF file
    chat_bot = PDFChatBot(pdf_path)
    query = "Ask your question here"  # replace this with the question you want to ask
    response = chat_bot.ask_question(query)
    print(response)


if __name__ == "__main__":
    main()
