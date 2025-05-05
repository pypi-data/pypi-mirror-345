import requests
from functools import wraps

def connection_check(func):
    """Check if the server is accessible. `base_url` and `_is_connected` must be provided."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            requests.head(url=self.base_url, timeout=5)
            self._is_connected = True
            return func(self, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self._is_connected = False
            return []
    return wrapper
