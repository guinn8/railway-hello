import json, os
from typing import Optional
from .artifact import Artifact
from .llm import call_llm, llm

# -------- helper for DALL·E images --------
async def _dalle_image(prompt: str) -> str:
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

# -------- concrete Builders (deterministic ↔ cacheable) --------
async def build_page(_: str) -> Artifact:
    page = await call_llm("create_page", {"n_ads": 3})
    return Artifact("json", json.dumps(page).encode())

async def build_ad(key: str) -> Artifact:
    _, hint = key.split(":", 1)  # key looks like "make_ad:foo"
    resp = await call_llm("make_ad", {"hint": hint} if hint else None)
    return Artifact("html", resp["html"].encode())

async def build_image(key: str) -> Artifact:
    _, prompt = key.split(":", 1)
    html = await _dalle_image(prompt or "retro computer art")
    return Artifact("html", html.encode())

builders = {
    "create_page": build_page,
    "make_ad":     build_ad,
    "make_image":  build_image,
}
