
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import os, json

from utils_hash import cache_key
from rate_limit import TokenBucket
from cache_mem import TTLCache
from mock_llm import MockLLM

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
RESPONSE_TTL_SECONDS = int(os.getenv("RESPONSE_TTL_SECONDS", "300"))
RATE_LIMIT_RPS = int(os.getenv("RATE_LIMIT_RPS", "5"))
RATE_LIMIT_BURST = int(os.getenv("RATE_LIMIT_BURST", "10"))

app = FastAPI(title="Week09 Mini Chatbot API")

bucket = TokenBucket(rate_per_sec=RATE_LIMIT_RPS, burst=RATE_LIMIT_BURST)
cache = TTLCache(ttl_seconds=RESPONSE_TTL_SECONDS)
llm = MockLLM()

class ChatRequest(BaseModel):
    userId: str = Field(..., description="사용자 식별자")
    message: str = Field(..., description="프롬프트/메시지")
    params: dict = Field(default_factory=dict, description="샘플링 파라미터 등 선택값")

@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    rl_key = f"{client_ip}:{req.userId}"
    if not bucket.allow(rl_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    key = cache_key({"message": req.message, "params": req.params}, MODEL_NAME)
    cached = cache.get(key)
    if cached:
        return JSONResponse({"cached": True, "model": MODEL_NAME, "output": cached})

    # (옵션) OpenAI 호출 자리 — 현재는 MockLLM 사용
    text = await llm.generate(req.message, max_tokens=128)
    cache.set(key, text)
    return {"cached": False, "model": MODEL_NAME, "output": text}

@app.post("/chat/stream")
async def chat_stream(req: ChatRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    rl_key = f"{client_ip}:{req.userId}"
    if not bucket.allow(rl_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    async def streamer():
        first = True
        async for chunk in llm.stream(req.message, max_tokens=128):
            data = json.dumps({"delta": chunk, "done": False if first else None})
            first = False
            yield f"data: {data}\n\n"
        yield 'data: {"done": true}\n\n'

    headers = {"Content-Type": "text/event-stream"}
    return StreamingResponse(streamer(), headers=headers)
