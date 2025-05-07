from app.rag.llm.client import client as llm_client

def chat_only_llm():
    response = llm_client.generate_with_metrics("Hello, how are you?")
    print(response)


def chat_with_rag():
    pass


