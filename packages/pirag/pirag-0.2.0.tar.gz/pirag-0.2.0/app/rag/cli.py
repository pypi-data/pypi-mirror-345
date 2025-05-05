import app.rag.config as cfn
from loguru import logger

from app.rag.llm.service import doctor as doctor_llm
from app.rag.embedding.service import doctor as doctor_embedding
from app.rag.vector_store.service import doctor as doctor_vector_store

def chat():
    print("Chatting with the RAG system...")


def train():
    print("Training the RAG system...")


def test():
    print("Testing the RAG system...")


def doctor():
    logger.info("💚 Doctoring the RAG system...")

    # -- LLM Server
    logger.info("Checking the LLM server (OpenAI-compatible)...")
    doctor_llm()

    # -- Embedding Server
    logger.info("Checking the embedding server (OpenAI-compatible)...")
    doctor_embedding()

    # -- Vector Store
    logger.info("Checking the vector store server (Milvus)...")    
    doctor_vector_store()
