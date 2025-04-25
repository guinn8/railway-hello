# tests/test_llm.py
import pytest, app.llm as llm_mod

@pytest.mark.asyncio
async def test_call_llm_json_stubbed():
    out = await llm_mod.call_llm_json("any")
    assert out == {"html": "<p>hi</p>", "css": ""}
