import os, json
from openai import AsyncOpenAI
from .prompt import get_prompt

llm   = AsyncOpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def call_llm(name: str, vars: dict | None = None):
    messages = [
        {"role": "user", "content": get_prompt(name, **(vars or {}))}
    ]
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)
