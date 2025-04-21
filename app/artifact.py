from typing import NamedTuple

class Artifact(NamedTuple):
    type: str   # e.g. "html", "json", "css", "png"
    data: bytes
