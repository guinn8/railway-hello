# app/builders.py
import json, os
from .artifact import Artifact
from .llm import call_llm_json, llm
from .tools import Tool, tools

class AdTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="make_ad",
            registry=tools,
            placeholder="{{CALL:make_ad:YOUR_HINT}}",
        )

    async def __call__(self, arg: str) -> Artifact:
        prompt = """\
        Return a JSON object: {"html": "<div>…</div>"}  
        Provide one retro banner-ad fragment only.  
        No fences.
        """
        if arg:
            prompt += f' Base the creative on this hint: "{arg}".'
        resp = await call_llm_json(prompt)
        return Artifact("html", resp["html"].encode())

class ImageTool(Tool):
    def __init__(self) -> None:
        super().__init__(
            name="make_image",
            registry=tools,
            placeholder="{{CALL:make_image:YOUR_PROMPT}}",
        )

    async def _dalle_image(self, prompt: str) -> str:
        resp = await llm.images.generate(
            model=os.getenv("DALLE_MODEL", "dall-e-2"),
            prompt=prompt,
            n=1,
            size="256x256",
        )
        url = resp.data[0].url
        safe_alt = prompt.replace('"', "")
        return f'<figure class="retro-img"><img src="{url}" alt="{safe_alt}"></figure>'
    
    async def __call__(self, arg: str) -> Artifact:
        html = await self._dalle_image(arg)
        return Artifact("html", html.encode())

AdTool()
ImageTool()