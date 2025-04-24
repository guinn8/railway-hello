# main.py
import os, re, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from app.store import store
from app.expander import expand
from app.artifact import Artifact
from app.llm import call_llm
from app.builders import AdTool, ImageTool

app = FastAPI()

async def build_page(_: str) -> Artifact:
    """Ask the LLM to create the entire page from the static prompt above."""

    CREATE_PAGE_BASE = """\
    You are building a retro download page.
    Do NOT include <script> tags.
    Include exactly 1 {{CALL:make_ad:…}} placeholders and 0 {{CALL:make_image:…}} placeholder.
    Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
    """
    AdTool()
    ImageTool()

    page = await call_llm(CREATE_PAGE_BASE.strip())
    return Artifact("json", json.dumps(page).encode())

@app.get("/", response_class=HTMLResponse)
async def root():
    art = await store.get("create_page:", build_page)
    page = json.loads(art.data)

    SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
    body = SCRIPT_RE.sub("", await expand(page["html"]))
    css = page.get("css", "")

    html = (
        "<!doctype html><html><head><title>Retro-DL</title>"
        f"<style>{css}</style></head><body>{body}</body></html>"
    )
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
