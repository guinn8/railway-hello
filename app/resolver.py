# app/resolver.py
import os, re, asyncio
from .llm import call_llm, llm   # re‑use AsyncOpenAI instance

PATTERN = re.compile(r"\{\{CALL:(\w+)(?::([^}]+))?\}\}")

async def _dalle_image(prompt: str) -> str:
    """Generate one DALL·E image and wrap it in inlinable HTML."""
    resp = await llm.images.generate(
        model=os.getenv("DALLE_MODEL", "dall-e-2"),
        prompt=prompt,
        n=1,
        size="256x256",
        quality="standard"
    )
    url = resp.data[0].url
    safe_alt = prompt.replace('"', "")
    return f'<figure class="retro-img"><img src="{url}" alt="{safe_alt}"></figure>'

async def _replace_batch(html: str):
    matches = list(PATTERN.finditer(html))
    if not matches:
        return html, False

    async def _dispatch(fn_name: str, hint: str | None):
        if fn_name == "make_image":
            # hint **must** exist because create_page enforces it
            return await _dalle_image(hint or "retro computer art")
        # default: LLM‑powered fragment
        return await call_llm(fn_name, {"hint": hint} if hint else None)

    tasks = [_dispatch(*m.groups()) for m in matches]
    results = await asyncio.gather(*tasks)

    parts, last = [], 0
    for m, snippet in zip(matches, results):
        parts.append(html[last : m.start()])
        parts.append(snippet)
        last = m.end()
    parts.append(html[last:])
    return "".join(parts), True

async def resolve(html: str) -> str:
    changed = True
    while changed:
        html, changed = await _replace_batch(html)
    return html
