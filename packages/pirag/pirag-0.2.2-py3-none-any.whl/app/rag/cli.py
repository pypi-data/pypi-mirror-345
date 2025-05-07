import app.rag.config as cfn
from loguru import logger

from app.rag.llm.services import doctor as doctor_llm
from app.rag.embedding.services import doctor as doctor_embedding
from app.rag.vector_store.services import doctor as doctor_vector_store
from app.rag.agent.services import chat_only_llm, chat_with_rag

def chat(options: dict):
    logger.debug(f"Chat parser options: {options}")
    no_rag = options.get('no_rag', False)

    # -- Chat
    if no_rag:
        logger.info("💬 Chatting with the LLM system directly...")
        chat_only_llm()
    else:
        logger.info("💬 Chatting with the RAG system...")
        chat_with_rag()


def train(options: dict):
    print("Training the RAG system...")
    logger.debug(f"Train parser options: {options}")


def test(options: dict):
    print("Testing the RAG system...")
    logger.debug(f"Test parser options: {options}")


def doctor(options: dict):
    logger.info("💚 Doctoring the RAG system...")
    
    logger.debug(f"Doctor parser options: {options}")
    # Check if resolve option is present
    resolve = options.get('resolve', False)
    if resolve:
        logger.info("🔧 Resolving issues is enabled")

    # -- LLM Server
    logger.info("🔍 Checking the LLM server (OpenAI-compatible)...")
    doctor_llm(resolve)

    # -- Embedding Server
    logger.info("🔍 Checking the embedding server (OpenAI-compatible)...")
    doctor_embedding(resolve)

    # -- Vector Store
    logger.info("🔍 Checking the vector store server (Milvus)...")    
    doctor_vector_store(resolve)

    if resolve:
        logger.info(f"🔧 Resolving issue completed. To make sure the issues are resolved, please try doctoring again.")
