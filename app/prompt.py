# app/prompt.py
from typing import Callable

def _create_page(n_ads: int) -> str:
    return (
        "You are building a retro download page. "
        "Do NOT include <script> tags. "
        f"Include exactly {n_ads} literal placeholders '{{{{CALL:make_ad}}}}' in the HTML. "
        "Return a JSON object: {\"html\": \"...\"} — **no markdown fences**."
    )

def _make_ad() -> str:
    return (
        "Return a JSON object: {\"html\": \"<div>…</div>\"}. "
        "Provide one retro banner‑ad fragment only. No fences."
    )

PROMPTS: dict[str, Callable[..., str]] = {
    "create_page": _create_page,
    "make_ad": _make_ad,
}

def get_prompt(name: str, **kw) -> str:
    try: return PROMPTS[name](**kw)
    except KeyError as e: raise ValueError(f"prompt '{name}' not found") from e
