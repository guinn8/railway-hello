import re, asyncio
from .store import store
from .tools import tools

TOKEN_RE = re.compile(r"\{\{CALL:([^}:]+)(?::([^}]*))?\}\}")

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

async def expand_stream(src: str):
    """
    Async generator that yields pieces of *src* as soon as they are available.
    Placeholder calls are launched in parallel but emitted in order.
    """
    tasks = []
    spans = []

    for m in TOKEN_RE.finditer(src):
        fn, arg = m.group(1), (m.group(2) or "")
        tasks.append(asyncio.create_task(store.get(f"{fn}:{arg}", tools[fn])))
        spans.append((m.start(), m.end()))

    pos = 0
    for (start, end), t in zip(spans, tasks):
        lit = src[pos:start]
        if lit:
            yield lit
        art = await t
        yield art.data.decode()
        pos = end

    tail = src[pos:]
    if tail:
        yield tail
