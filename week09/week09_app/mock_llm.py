
import asyncio

class MockLLM:
    def __init__(self, delay_ms_per_token: int = 40):
        self.delay = delay_ms_per_token / 1000.0

    async def generate(self, prompt: str, max_tokens: int = 64):
        text = "[MOCK] " + (prompt[::-1])[:max_tokens]
        await asyncio.sleep(self.delay * max(1, min(len(text)//6, 10)))
        return text

    async def stream(self, prompt: str, max_tokens: int = 64):
        text = await self.generate(prompt, max_tokens)
        chunks = max(1, min(8, len(text)//max(1, len(text)//8)))
        step = max(1, len(text)//chunks)
        for i in range(0, len(text), step):
            await asyncio.sleep(self.delay)
            yield text[i:i+step]
