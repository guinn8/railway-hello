import os, re
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from app.llm import call_llm
from app.resolver import resolve
from app.prompt import get_prompt

SCRIPT_RE = re.compile(r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>", re.I)
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    sys_msg = get_prompt("create_page", n_ads=3)          # ← tidy getter
    page = await call_llm("create_page", {}, sys=sys_msg)
    body = SCRIPT_RE.sub("", await resolve(page["body_html"]))
    html = f'<!doctype html><html><head><title>{page["title"]}</title></head><body>{body}</body></html>'
    return HTMLResponse(html)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
