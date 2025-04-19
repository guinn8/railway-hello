"""
Central prompt+schema store, expressed as JSON literals so you can
edit them like a config file.  import get_prompt() or FUNCTION_SCHEMA.
"""
import json, functools

# -------------- raw JSON blocks ------------------------------------
_PROMPT_JSON = """{
  "create_page": [
    "You are building a retro download page.",
    "Do NOT include inline <script> tags.",
    "Include exactly {n_ads} literal placeholders '{{{{CALL:make_ad}}}}' inside body_html."
  ],
  "make_ad": [
    "Return a single retro banner ad fragment in HTML."
  ]
}"""

_FUNCTION_SCHEMA_JSON = """[
  {
    "name": "create_page",
    "description": "Start a new HTML page",
    "parameters": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "body_html": {"type": "string"}
      },
      "required": ["title", "body_html"]
    }
  },
  {
    "name": "make_ad",
    "description": "Generate a single banner‑ad fragment",
    "parameters": {
      "type": "object",
      "properties": {
        "html": {"type": "string"}
      },
      "required": ["html"]
    }
  }
]"""

# -------------- parsed objects -------------------------------------
_PROMPTS        = json.loads(_PROMPT_JSON)
FUNCTION_SCHEMA = json.loads(_FUNCTION_SCHEMA_JSON)

# -------------- public helper --------------------------------------
@functools.lru_cache(maxsize=None)
def get_prompt(section: str, **params) -> str:
    """
    Retrieve a concatenated prompt string.
    Placeholder tokens like {n_ads} are formatted with **params.
    """
    try:
        lines = _PROMPTS[section]
    except KeyError as e:
        raise ValueError(f"Prompt section '{section}' not found") from e
    if not isinstance(lines, list):
        lines = [lines]
    return " ".join(line.format(**params) for line in lines)
