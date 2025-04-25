# main.py
import os, re, json, time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

from app.store import store
from app.expander import expand, expand_stream
from app.artifact import Artifact
from app.llm import call_llm_json, call_llm
from app.builders import AdTool, ImageTool

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>", re.I)
app = FastAPI()


# ─────────────────────────────────────────────────────────────
# Page builder  →  returns *async generator* of html chunks
# ─────────────────────────────────────────────────────────────
async def build_page(intro: str):
    prompt = (
        intro
        + "\n\n(Return everything below strictly as **json**.)\n"
        + """
Do NOT include <script> tags.
Include exactly
1 {{CALL:make_ad:…}} placeholder and
0 {{CALL:make_image:…}} placeholders.
Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
"""
    )
    page = await call_llm_json(prompt.strip())
    obj = page if isinstance(page, dict) else json.loads(page)

    # strip any <script> the LLM might have snuck in
    body_src = SCRIPT_RE.sub("", obj["html"])
    css      = obj.get("css", "")

    head = (
        "<!doctype html><html><head><title>Retro-DL</title>"
        f"<style>{css}</style></head><body>"
    )
    tail = "</body></html>"

    async def _generator():
        yield head
        async for chunk in expand_stream(body_src):
            yield chunk
        yield tail

    return _generator()          # an *async generator* object


# ─────────────────────────────────────────────────────────────
# Route “/” — buffered by default, stream if header set
# ─────────────────────────────────────────────────────────────
@app.get("/")
async def root(request: Request):
    intro = await call_llm(
        "give me a cool idea man, like water ballon but never say that."
    )

    # --- streaming branch -------------------------------------------------
    if request.headers.get("X-Stream") == "1":
        gen = await build_page(intro)          # no caching for now
        return StreamingResponse(gen, media_type="text/html")

    # --- buffered branch  (cached via store) ------------------------------
    async def builder(_: str) -> Artifact:
        g = await build_page(intro)
        html = "".join([part async for part in g])
        return Artifact("html", html.encode())

    art = await store.get("create_page:", builder)
    return HTMLResponse(art.data.decode())


# ─────────────────────────────────────────────────────────────
# Legacy streaming demo (kept until Patch 4 cleanup)
# ─────────────────────────────────────────────────────────────
from app.llm import stream_llm

@app.get("/stream-demo")
async def stream_demo():
    return StreamingResponse(stream_llm("pong"), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
