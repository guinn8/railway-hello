# main.py
import os, re, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

from app.store import store
from app.expander import expand
from app.artifact import Artifact
from app.llm import call_llm_json, call_llm, stream_llm
from app.builders import AdTool, ImageTool

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

async def build_page(intro: str) -> Artifact:
    prompt = (
        intro
        + "\n\n(Return everything below strictly as **json**.)\n"
        + """
Do NOT include <script> tags.
Include exactly 
1 {{CALL:make_ad:…}} placeholder and 
0 {{CALL:make_image:…}} placeholders.
Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
""")
    page = await call_llm_json(prompt.strip())
    obj = page if isinstance(page, dict) else json.loads(page)
    body = SCRIPT_RE.sub("", await expand(obj["html"]))
    css = obj.get("css", "")
    html = (
        "<!doctype html><html><head><title>Retro-DL</title>"
        f"<style>{css}</style></head><body>{body}</body></html>"
    )
    return Artifact("html", html.encode())

@app.get("/", response_class=HTMLResponse)
async def root():
    intro = await call_llm("give me a cool idea man, like water ballon but never say that.")
    async def builder(_: str) -> Artifact:
        return await build_page(intro)
    art = await store.get("create_page:", builder)
    return HTMLResponse(art.data.decode())

# ---------- NEW demo route ----------
@app.get("/stream-demo")
async def stream_demo():
    return StreamingResponse(stream_llm("pong"), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
