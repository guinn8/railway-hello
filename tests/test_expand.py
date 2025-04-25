# tests/test_expand.py
import pytest
from app.expander import expand
from app.artifact import Artifact
from app.tools import tools, Tool

class DummyTool(Tool):
    def __init__(self):
        super().__init__("dummy", tools, "{{CALL:dummy:YOUR_HINT}}")

    async def __call__(self, arg: str) -> Artifact:
        return Artifact("html", b"OK")

@pytest.mark.asyncio
async def test_expand_replaces_placeholder():
    DummyTool()  # registers into `tools`
    res = await expand("A{{CALL:dummy:}}B")
    print(res)
    assert res == "AOKB"
