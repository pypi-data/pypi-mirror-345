import requests
import time
from langchain_openai.llms import OpenAI
from typing import Dict, Tuple, Any, List, Optional

import app.rag.config as cfn
from app.rag.utilities import connection_check
from .utilities import MetricCallbackHandler

class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self._is_connected = True
        self._client = None
        
        if self.check_connection():
            try:
                self._client = OpenAI(
                    base_url = base_url,
                    api_key = api_key,
                    model = model
                )
            except Exception as e:
                self._is_connected = False
    
    def check_connection(self) -> bool:
        """Check if the LLM server is accessible"""
        try:
            requests.head(url=self.base_url, timeout=5)
        except requests.exceptions.ConnectionError:
            self._is_connected = False
            return False
        self._is_connected = True
        return True
    
    @connection_check
    def generate(self, prompt: str) -> tuple:
        """Generate text from prompt and return usage information
        
        Returns:
            tuple: (generated_text, usage_info)
        """
        if not self._is_connected or self._client is None:
            return "", {}
        
        response = self._client.generate([prompt])
        return response.generations[0][0].text, response.llm_output
    
    @connection_check
    def generate_with_metrics(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Generate text with timing and usage metrics
        
        Returns:
            tuple: (generated_text, metrics_info)
        """
        if not self._is_connected or self._client is None:
            return "", {"error": "LLM client not connected"}
        
        handler = MetricCallbackHandler()
        
        # Create streaming client with callback
        streaming_client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model,
            streaming=True,
            callbacks=[handler]
        )
        
        # Make a single request
        response = streaming_client.generate([prompt], callbacks=[handler])
        
        # Get base metrics from response
        metrics = {}
        
        # Extract token usage from response
        llm_output = response.llm_output if hasattr(response, 'llm_output') else {}
        
        # Check if token_usage exists in the response
        token_usage = llm_output.get('token_usage', {})
        if token_usage:
            # If token_usage is available, copy it to our metrics
            metrics.update(token_usage)
        
        # Add model name if available
        if 'model_name' in llm_output:
            metrics['model'] = llm_output['model_name']
        else:
            metrics['model'] = self.model
        
        # Calculate and add timing metrics
        metrics['ttft'] = handler.ttft or 0.0
        metrics['total_time'] = (handler.end_time or time.time()) - handler.start_time
        metrics['tokens_per_second'] = handler.calculate_tokens_per_second()
        metrics['completion_tokens'] = handler.token_count
        
        return handler.result, metrics
    
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

client = LLMClient(
    base_url = cfn.LLM_BASE_URL,
    api_key = cfn.LLM_API_KEY,
    model = cfn.LLM_MODEL,
)
