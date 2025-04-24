# main.py
import os, re, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from app.store import store
from app.expander import expand

from app.artifact import Artifact
from app.llm import call_llm, llm
from app.tools import Tool, tools
from app.builders import AdTool, ImageTool


SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

AdTool()
ImageTool()

async def build_page(_: str) -> Artifact:
    """Ask the LLM to create the entire page from the static prompt above."""

    CREATE_PAGE_BASE = """\
    You are building a retro download page.
    Do NOT include <script> tags.
    Include exactly 3 {{CALL:make_ad:…}} placeholders and 1 {{CALL:make_image:…}} placeholder.
    Return a JSON object: {"html": "...", "css": "..."} — no markdown fences.
    """

    page = await call_llm(CREATE_PAGE_BASE.strip())
    return Artifact("json", json.dumps(page).encode())

@app.get("/", response_class=HTMLResponse)
async def root():
    # Fetch (or build+cache) the page artifact directly via build_page
    art = await store.get("create_page:", build_page)
    page = json.loads(art.data)

    # Expand all {{CALL:...}} tokens in the HTML
    body = SCRIPT_RE.sub("", await expand(page["html"]))
    css = page.get("css", "")

    html = (
        "<!doctype html><html><head><title>Retro-DL</title>"
        f"<style>{css}</style></head><body>{body}</body></html>"
    )
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
