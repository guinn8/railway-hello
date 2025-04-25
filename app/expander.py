# app/expander.py
import re
from .store import store
from .tools import tools

TOKEN_RE = re.compile(r"\{\{CALL:([^}:]+)(?::([^}]*))?\}\}")

# ---------- buffered helper (unchanged) ----------
async def expand(src: str) -> str:
    while True:
        matches = list(TOKEN_RE.finditer(src))
        if not matches:
            return src

        parts, last = [], 0
        for m in matches:
            fn, arg = m.group(1), (m.group(2) or "")
            tool = tools[fn]
            art = await store.get(f"{fn}:{arg}", tool)
            parts.append(src[last:m.start()])
            parts.append(art.data.decode())
            last = m.end()
        parts.append(src[last:])
        src = "".join(parts)

# ---------- NEW: streamed version ----------
async def expand_stream(src: str):
    """
    Async generator that yields pieces of *src* as soon as they are available.
    For every {{CALL:tool:arg}} placeholder:
        • yield preceding literal HTML
        • await tool(arg) once, then yield its html
    """
    pos = 0
    for m in TOKEN_RE.finditer(src):
        # literal chunk before the tool call
        literal = src[pos : m.start()]
        if literal:
            yield literal

        fn, arg = m.group(1), (m.group(2) or "")
        art = await store.get(f"{fn}:{arg}", tools[fn])
        yield art.data.decode()

        pos = m.end()

    # tail after the last placeholder
    tail = src[pos:]
    if tail:
        yield tail
