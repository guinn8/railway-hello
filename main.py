# main.py
import os, re, json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from app.store import store
from app.builders import builders
from app.expander import expand

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    # Fetch the top-level page artifact
    art = await store.get("create_page:", builders["create_page"])
    page = json.loads(art.data)

    # Expand all {{CALL:...}} tokens in the HTML
    body = SCRIPT_RE.sub("", await expand(page["html"]))
    css = page.get("css", "")

    html = f"<!doctype html><html><head><title>Retro‑DL</title><style>{css}</style></head><body>{body}</body></html>"
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
