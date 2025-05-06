from chatgpt.enums import Endpoint, OpenAIModels, Role
from chatgpt.errors import OpenAIAPIError
from ..types import GeneralDict
from ._base import Base


class GPT4oMini(Base):
    def __init__(self, api_key: str, temperature: float = 1) -> None:
        super().__init__(
            api_key,
            OpenAIModels.GPT_35_TURBO,
            Endpoint.CHAT_COMPLETION_V1,
            temperature=temperature,
        )

    async def system_prompt(self, prompt: str) -> str:
        data: GeneralDict = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": [
                {"role": Role.SYSTEM, "content": prompt},
            ],
        }

        resp = await self._request(data)
        if resp.get("error", False):
            raise OpenAIAPIError(f"Open AI ChatGPT API says: {resp}")
        return str(resp["choices"][0]["message"]["content"])
