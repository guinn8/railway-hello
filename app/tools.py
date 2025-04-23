# app/tools.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict
from .artifact import Artifact

class Tool(ABC):
    """
    Base class for every templating/expansion command.

    Parameters
    ----------
    name : str
        Command name used inside the {{CALL:...}} placeholder.
    registry : Dict[str, Tool]
        Central registry where the tool auto-registers itself.
    placeholder : str
        Example placeholder that authors should copy verbatim
        (use ALL-CAPS words like YOUR_HINT for free text).
    page_requirement : int | None, default None
        If not-None, the page that references this tool **must** contain
        exactly this many placeholders of `placeholder` form.
    """
    def __init__(
        self,
        name: str,
        registry: Dict[str, "Tool"],
        placeholder: str,
        page_requirement: int | None = None,
    ) -> None:
        self.name = name
        self.placeholder = placeholder
        self.page_requirement = page_requirement
        registry[name] = self

    # ---------- contract that concrete tools must implement ----------
    @abstractmethod
    async def __call__(self, arg: str) -> Artifact: ...

# single global catalogue
tools: Dict[str, Tool] = {}
