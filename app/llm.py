import os, json
from openai import AsyncOpenAI
from .prompt import FUNCTION_SCHEMA  # ← NEW

llm = AsyncOpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def call_llm(name: str, args: dict | None = None, sys: str | None = None):
    resp = await llm.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": sys or ""}],
        functions=FUNCTION_SCHEMA,                   # ← now shared
        function_call={"name": name, "arguments": json.dumps(args or {})}
    )
    return json.loads(resp.choices[0].message.function_call.arguments)
