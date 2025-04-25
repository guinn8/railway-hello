# app/llm.py
import os, json
from openai import AsyncOpenAI

llm   = AsyncOpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def call_llm_json(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

async def call_llm(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return resp.choices[0].message.content

# ---------- NEW: streaming helper ----------
async def stream_llm(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    stream = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        if getattr(delta, "content", None):
            yield delta.content
