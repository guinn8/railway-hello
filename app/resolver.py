# app/resolver.py
import re, asyncio
from .llm import call_llm

PATTERN = re.compile(r"\{\{CALL:(\w+)(?::([^}]+))?\}\}")

async def _replace_batch(html: str):
    matches = list(PATTERN.finditer(html))
    if not matches:
        return html, False
    tasks = [
        call_llm(m.group(1), {"hint": m.group(2)}) if m.group(2) else call_llm(m.group(1))
        for m in matches
    ]
    results = await asyncio.gather(*tasks)
    parts, last = [], 0
    for m, snippet in zip(matches, results):
        parts.append(html[last:m.start()])
        parts.append(snippet)
        last = m.end()
    parts.append(html[last:])
    return "".join(parts), True

async def resolve(html: str) -> str:
    changed = True
    while changed:
        html, changed = await _replace_batch(html)
    return html
