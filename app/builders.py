# app/builders.py
import json, os
from .artifact import Artifact
from .llm import call_llm, load_prompt, llm   # keep existing import order

# -------- helper for DALL·E images --------
async def _dalle_image(prompt: str) -> str:
    resp = await llm.images.generate(
        model=os.getenv("DALLE_MODEL", "dall-e-2"),
        prompt=prompt,
        n=1,
        size="256x256",
    )
    url = resp.data[0].url
    safe_alt = prompt.replace('"', "")
    return f'<figure class="retro-img"><img src="{url}" alt="{safe_alt}"></figure>'

# -------- concrete Builders (deterministic ↔ cacheable) --------
async def build_page(_: str) -> Artifact:
    base = load_prompt("create_page")
    # tack on templating instructions without string-format placeholders
    prompt = (
        f"{base}\n\n"
        "Include exactly 3 literal placeholders of the form "
        "'{{CALL:make_ad}}' **or** '{{CALL:make_ad:YOUR_HINT}}'. "
        "Also include **exactly one** image placeholder of the form "
        "'{{CALL:make_image:YOUR_PROMPT}}'."
    )
    page = await call_llm(prompt)
    return Artifact("json", json.dumps(page).encode())

async def build_ad(key: str) -> Artifact:
    _, hint = key.split(":", 1)              # key looks like "make_ad:foo"
    base = load_prompt("make_ad")
    extra = f' Base the creative on this hint: "{hint}".' if hint else ""
    prompt = f"{base}{extra}"
    resp = await call_llm(prompt)
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
