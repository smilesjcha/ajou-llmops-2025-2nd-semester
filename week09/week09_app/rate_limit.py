
import time
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate_per_sec: int, burst: int):
        self.rate = rate_per_sec
        self.burst = burst
        self.tokens = defaultdict(lambda: burst)
        self.timestamps = defaultdict(lambda: time.time())

    def allow(self, key: str) -> bool:
        now = time.time()
        last = self.timestamps[key]
        delta = now - last
        refill = delta * self.rate
        self.tokens[key] = min(self.burst, self.tokens[key] + refill)
        self.timestamps[key] = now
        if self.tokens[key] >= 1:
            self.tokens[key] -= 1
            return True
        return False
