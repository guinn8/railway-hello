# main.py
import os, re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from app.llm import call_llm
from app.resolver import resolve

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    body = await call_llm("create_page", {"n_ads": 3})
    body = SCRIPT_RE.sub("", await resolve(body))
    html = f"<!doctype html><html><head><title>Retro‑DL</title></head><body>{body}</body></html>"
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
