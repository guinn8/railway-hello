# main.py
import os, re, json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

from app.expander import expand_stream
from app.llm import call_llm_json, call_llm
from app.builders import AdTool, ImageTool    # ensure tools are registered

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", re.I)
app = FastAPI()


# ─────────────────────────────────────────────────────────────
# Streaming page builder → yields head, expanded body, tail
# ─────────────────────────────────────────────────────────────
async def build_page(intro: str):
    prompt = (
        intro
        + "\n\n(Return everything below strictly as **json**.)\n"
        + """
        Make something ambitious for your client!
Include exactly 2 {{CALL:make_ad:…}} placeholder and include exactly 2  {{CALL:make_image:…}} placeholders.
Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
"""
    )
    page = await call_llm_json(prompt.strip())
    obj = page if isinstance(page, dict) else json.loads(page)

    body_src = SCRIPT_RE.sub("", obj["html"])
    css      = obj.get("css", "")

    head = (
        "<!doctype html><html><head><title>_internet_</title>"
        f"<style>{css}</style></head><body>"
    )
    tail = "</body></html>"

    async def _gen():
        yield head
        async for chunk in expand_stream(body_src):
            yield chunk
        yield tail

    return _gen()


# ─────────────────────────────────────────────────────────────
# Single route – always streaming
# ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():

    intro = await call_llm(
        "give me a cool idea man, like water ballon or mechanical frog but never say that. I'm not looking for a business it could be an existing but interesting historical event, product, or strange concept."
    )
    gen = await build_page(intro)
    return StreamingResponse(gen, media_type="text/html")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
