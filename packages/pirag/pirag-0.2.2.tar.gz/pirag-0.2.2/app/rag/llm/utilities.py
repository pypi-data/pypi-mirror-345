import time
from langchain.callbacks.base import BaseCallbackHandler

class MetricCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.start_time = time.time()
        self.ttft = None
        self.first_token_time = None
        self.result = ""
        self.end_time = None
        self.token_count = 0
        self.token_timestamps = []
    
    def on_llm_new_token(self, token: str, **kwargs):
        current_time = time.time()
        self.token_count += 1
        self.token_timestamps.append(current_time)
        
        if self.ttft is None:
            self.ttft = current_time - self.start_time
            self.first_token_time = current_time
            
        self.result += token
    
    def on_llm_end(self, *args, **kwargs):
        self.end_time = time.time()
    
    def calculate_tokens_per_second(self):
        """Calculate tokens per second after the first token"""
        if self.token_count <= 1 or self.first_token_time is None or self.end_time is None:
            return 0.0
        
        # Calculate time from first token to completion (exclude TTFT)
        generation_time = self.end_time - self.first_token_time
        if generation_time <= 0:
            return 0.0
        
        # Exclude the first token from the count since we're measuring from after it arrived
        tokens_after_first = self.token_count - 1
        return tokens_after_first / generation_time
