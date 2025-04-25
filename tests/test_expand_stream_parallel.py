# tests/test_expand_stream_parallel.py
import time, asyncio, pytest
from app.artifact import Artifact
from app.tools import tools, Tool
from app.expander import expand_stream

class SlowTool(Tool):
    """A tool that sleeps for 50 ms and returns its arg unchanged."""
    def __init__(self):
        super().__init__("slow", tools, "{{CALL:slow:YOUR_HINT}}")

    async def __call__(self, arg: str) -> Artifact:
        await asyncio.sleep(0.05)          # simulate network / OpenAI latency
        return Artifact("html", arg.encode())

@pytest.mark.asyncio
async def test_expand_stream_is_parallel():
    SlowTool()                            # register once

    html = "{{CALL:slow:A}}{{CALL:slow:B}}"   # two sequential placeholders
    t0   = time.perf_counter()
    chunks = [chunk async for chunk in expand_stream(html)]
    dt   = time.perf_counter() - t0

    # output must preserve order and content
    assert "".join(chunks) == "AB"

    # serial execution would take ≈0.10 s; parallel should be ≈0.05 s
    assert dt < 0.09, f"tool calls ran serially: {dt:.3f}s"
