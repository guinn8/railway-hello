# main.py
import os, re, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

from app.expander import expand
from app.artifact import Artifact
from app.llm import call_llm

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

async def build_page(intro: str) -> Artifact:
    prompt = intro + """
    Do NOT include <script> tags.
    Include exactly 2 {{CALL:make_ad:…}} placeholders and 1 {{CALL:make_image:…}} placeholder.
    Return a JSON object: {{"html": "...", "css": "..."}} — no markdown fences."""
    page = await call_llm(prompt)
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
    art = await build_page("You are building a retro download page.")
    return HTMLResponse(art.data.decode())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
