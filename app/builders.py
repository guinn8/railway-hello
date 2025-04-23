# app/builders.py
import json, os
from .artifact import Artifact
from .llm import call_llm, llm
from .tools import Tool, tools

# ------------------------------------------------------------
# Inline base‐prompts
CREATE_PAGE_BASE = """\
You are building a retro download page.
Do NOT include <script> tags.
Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
"""

MAKE_AD_BASE = """\
Return a JSON object: {"html": "<div>…</div>"}  
Provide one retro banner-ad fragment only.  
No fences.
"""
# ------------------------------------------------------------

# helper for DALL·E images (unchanged)
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

# -------- concrete tools -------------------------------------------------
class AdTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="make_ad",
            registry=tools,
            placeholder="{{CALL:make_ad:YOUR_HINT}}",
            page_requirement=3,
        )

    async def __call__(self, arg: str) -> Artifact:
        prompt = MAKE_AD_BASE
        if arg:
            prompt += f' Base the creative on this hint: "{arg}".'
        resp = await call_llm(prompt)
        return Artifact("html", resp["html"].encode())


class ImageTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="make_image",
            registry=tools,
            placeholder="{{CALL:make_image:YOUR_PROMPT}}",
            page_requirement=1,
        )

    async def __call__(self, arg: str) -> Artifact:
        html = await _dalle_image(arg or "retro computer art")
        return Artifact("html", html.encode())


# register tools once on import
AdTool()
ImageTool()


# ====================== dynamic page‐builder ======================
async def build_page(_: str) -> Artifact:
    """
    Ask the LLM to create the page using each Tool’s metadata
    instead of hard‐coding placeholders here.
    """
    # Start with the static page prompt
    prompt = CREATE_PAGE_BASE.strip() + "\n\n"

    # Append each Tool’s requirement rule
    for t in tools.values():
        if t.page_requirement is None:
            continue
        n = t.page_requirement
        plural = "s" if n != 1 else ""
        prompt += (
            f"Include exactly {n} placeholder{plural} "
            f"of the form '{t.placeholder}'. "
        )

    page = await call_llm(prompt.strip())
    return Artifact("json", json.dumps(page).encode())


# Exposed for main.py’s `store.get("create_page:", builders["create_page"])`
builders = {
    "create_page": build_page,
}
