pytest_plugins = ("pytest_asyncio",)   # ensure the plugin is loaded

import types, pytest, json, app.llm as llm_mod

DUMMY_JSON = {"html": "<p>hi</p>", "css": ""}

@pytest.fixture(autouse=True)
def _stub_openai(monkeypatch):
    # stub *streaming* + normal create
    async def fake_chat_create(**_kw):
        # always respond with valid json content
        content = json.dumps(DUMMY_JSON)
        return types.SimpleNamespace(
            choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content))]
        )
    monkeypatch.setattr(llm_mod.llm.chat.completions, "create", fake_chat_create)

    # high-level helpers used elsewhere
    async def fake_json(_): return DUMMY_JSON
    async def fake_text(_): return "stub-idea"
    monkeypatch.setattr(llm_mod, "call_llm_json", fake_json)
    monkeypatch.setattr(llm_mod, "call_llm", fake_text)
