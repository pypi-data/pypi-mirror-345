from typing import Protocol


class ChatGPTModel(Protocol):

    async def system_prompt(self, prompt: str) -> str: ...
