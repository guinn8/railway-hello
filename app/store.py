import os, random, asyncio
from typing import Callable, Awaitable
from .artifact import Artifact

class Store:
    def __init__(self, quota: int | None = None):
        self._mem: dict[str, Artifact] = {}
        self._quota = quota or int(os.getenv("API_BUDGET", "10_000"))
        self._calls = 0

    async def get(self, key: str,
                  builder: Callable[[str], Awaitable[Artifact]]) -> Artifact:
        if key not in self._mem:
            if self._calls >= self._quota and self._mem:
                # budget exhausted → return random cached thing
                return random.choice(list(self._mem.values()))
            self._mem[key] = await builder(key)
            self._calls += 1
        return self._mem[key]

store = Store()
