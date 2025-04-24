# app/llm.py
import os, json, importlib.resources as pkg
from openai import AsyncOpenAI

llm   = AsyncOpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def call_llm(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)
