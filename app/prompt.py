# app/prompt.py
from typing import Callable

def _create_page(n_ads: int) -> str:
    return (
        "You are building a retro download page. "
        "Do **NOT** include <script> tags. "
        # ads
        f"Include exactly {n_ads} literal placeholders of the form "
        "'{{CALL:make_ad}}' **or** '{{CALL:make_ad:YOUR_HINT}}'. "
        # image
        "Also include **exactly one** image placeholder of the form "
        "'{{CALL:make_image:YOUR_PROMPT}}'. "
        'Return a JSON object: {"html": "..."} — no markdown fences.'
    )

def _make_ad(hint: str | None = None) -> str:
    return (
        'Return a JSON object: {"html": "<div>…</div>"}. '
        "Provide one retro banner‑ad fragment only. "
        + (f'Base the creative on this hint: "{hint}". ' if hint else "Free choice. ")
        + "No fences."
    )

PROMPTS: dict[str, Callable[..., str]] = {
    "create_page": _create_page,
    "make_ad": _make_ad,
    # make_image handled directly in resolver – no prompt needed
}

def get_prompt(name: str, **kw) -> str:
    try:
        return PROMPTS[name](**kw)
    except KeyError as e:
        raise ValueError(f"prompt '{name}' not found") from e
