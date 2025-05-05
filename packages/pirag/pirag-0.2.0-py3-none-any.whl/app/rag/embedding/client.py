import requests
from langchain_openai.embeddings import OpenAIEmbeddings

import app.rag.config as cfn
from app.rag.utils import connection_check


class EmbeddingClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self._is_connected = True
        self._client = None
        
        if self.check_connection():
            try:
                self._client = OpenAIEmbeddings(
                    base_url = base_url,
                    api_key = api_key,
                    model = model
                )
            except Exception as e:
                self._is_connected = False
    
    def check_connection(self) -> bool:
        """Check if the embedding server is accessible"""
        try:
            requests.head(url=self.base_url, timeout=5)
        except requests.exceptions.ConnectionError:
            self._is_connected = False
            return False
        self._is_connected = True
        return True
    
    @connection_check
    def generate(self, prompt: str) -> str:
        """Generate text from prompt"""
        if not self._is_connected or self._client is None:
            return ""
        return self._client.embed_query(prompt)
    
    @connection_check
    def list_models(self) -> list:
        """List available models"""
        if not self._is_connected:
            return []
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            if response.status_code == 200:
                return [model['id'] for model in response.json()['data']]
            return []
        except Exception:
            return []
    
    @connection_check
    def has_model(self, model: str) -> bool:
        """Check if model exists"""
        if not self._is_connected:
            return False
        return model in self.list_models()

client = EmbeddingClient(
    base_url = cfn.EMBEDDING_BASE_URL,
    api_key = cfn.EMBEDDING_API_KEY,
    model = cfn.EMBEDDING_MODEL,
)
