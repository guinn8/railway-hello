# app/expander.py
import re
from .store import store
from .tools import tools

TOKEN_RE = re.compile(r"\{\{CALL:([^}:]+)(?::([^}]+))?\}\}")

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
