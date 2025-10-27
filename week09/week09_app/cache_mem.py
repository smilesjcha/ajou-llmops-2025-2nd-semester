
import time

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self.store = {}

    def get(self, key: str):
        item = self.store.get(key)
        if not item: return None
        value, exp = item
        if exp < time.time():
            self.store.pop(key, None)
            return None
        return value

    def set(self, key: str, value):
        self.store[key] = (value, time.time() + self.ttl)
