# tests/conftest.py
pytest_plugins = ("pytest_asyncio",)

import types, pytest, json, app.llm as llm_mod

DUMMY_JSON = {"html": "<p>hi</p>", "css": ""}


@pytest.fixture(autouse=True)
def _stub_openai(monkeypatch):
    """
    Stubs ``llm.chat.completions.create`` so that:

    * normal call  → SimpleNamespace with .choices[0].message.content (JSON string)
    * stream=True  → async iterator that yields one delta chunk with ``"pong"``
    """

    async def fake_chat_create(*_, **kw):
        # ── streaming branch ───────────────────────────────────────────────
        if kw.get("stream"):
            async def _aiter():
                yield types.SimpleNamespace(
                    choices=[
                        types.SimpleNamespace(
                            delta=types.SimpleNamespace(content="pong")
                        )
                    ]
                )
            return _aiter()  # an object with __aiter__
        # ── buffered branch ────────────────────────────────────────────────
        content = json.dumps(DUMMY_JSON)
        return types.SimpleNamespace(
            choices=[
                types.SimpleNamespace(
                    message=types.SimpleNamespace(content=content)
                )
            ]
        )

    # low-level stub
    monkeypatch.setattr(llm_mod.llm.chat.completions, "create", fake_chat_create)

    # high-level helpers used elsewhere
    async def fake_json(_): return DUMMY_JSON
    async def fake_text(_): return "stub-idea"
    monkeypatch.setattr(llm_mod, "call_llm_json", fake_json)
    monkeypatch.setattr(llm_mod, "call_llm",      fake_text)
