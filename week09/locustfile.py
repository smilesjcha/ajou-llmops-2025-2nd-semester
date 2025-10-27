
from locust import HttpUser, task, between
import json, random, string

def rand_prompt(n=12):
    return ''.join(random.choices(string.ascii_letters + ' ', k=n))

class ChatUser(HttpUser):
    wait_time = between(0.5, 1.5)
    @task(3)
    def chat(self):
        payload = {"userId":"locust", "message": f"Hello {rand_prompt()}"}
        self.client.post("/chat", json=payload)
    @task(1)
    def stream(self):
        payload = {"userId":"locust", "message": f"Stream {rand_prompt()}"}
        self.client.post("/chat/stream", json=payload)
