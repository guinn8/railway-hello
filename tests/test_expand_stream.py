# tests/test_expand_stream.py
import pytest
from app.artifact import Artifact
from app.tools import tools, Tool
from app.expander import expand, expand_stream

class DummyTool(Tool):
    def __init__(self):
        super().__init__("dummy", tools, "{{CALL:dummy:YOUR_HINT}}")

    async def __call__(self, arg: str) -> Artifact:
        return Artifact("html", b"OK")

@pytest.mark.asyncio
async def test_expand_stream_matches_buffered():
    DummyTool()                         # register tool once
    html = "A{{CALL:dummy:}}B"

    # collect streamed chunks
    chunks = []
    async for part in expand_stream(html):
        chunks.append(part)

    streamed = "".join(chunks)
    buffered = await expand(html)

    assert streamed == buffered == "AOKB"
