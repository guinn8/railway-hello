# app/llm.py
import os, json
from openai import AsyncOpenAI
from .prompt import get_prompt

llm   = AsyncOpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def call_llm(name: str, vars: dict | None = None, sys: str | None = None) -> str:
    user_msg = get_prompt(name, **(vars or {}))
    messages = ([] if sys is None else [{"role": "system", "content": sys}]) + [
        {"role": "user", "content": user_msg}
    ]
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}    # ✅ forces JSON
    )
    return json.loads(resp.choices[0].message.content)["html"]
