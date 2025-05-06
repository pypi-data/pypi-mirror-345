import json
import aiohttp

from ..enums import BaseURL, Endpoint

from ..errors import OpenAIAPIError
from ..types import GeneralDict, RequestDataT, Role
from urllib.parse import urljoin


class TextGen:
    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        endpoint: str = Endpoint.CHAT_COMPLETION_V1,
        base_url: str = BaseURL.OPENAI,
        temperature: float = 1.0,
    ) -> None:
        self._api_key = api_key
        self._temperature = temperature
        self._model = model
        self._url = urljoin(base=base_url, url=endpoint)
        self._session = aiohttp.ClientSession()
        self._system_prompt = system_prompt

    def _get_headers(self) -> GeneralDict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        return headers

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

    async def _request(self, user_prompt: str, method: str = "POST") -> str:
        data: RequestDataT = {
            "model": self._model,
            "temperature": self._temperature,
            "messages": [
                {
                    "role": Role.DEVELOPER,
                    "content": [{"type": "text", "text": self._system_prompt}],
                },
                {"role": Role.USER, "content": [{"type": "text", "text": user_prompt}]},
            ],
        }
        async with self._session.request(
            method=method,
            url=self._url,
            headers=self._get_headers(),
            data=json.dumps(data),
        ) as resp:
            await resp.read()

        js_resp = dict(await resp.json())

        if js_resp.get("error", False):
            raise OpenAIAPIError(f"Open AI ChatGPT API says: {await resp.text()}")

        return str(js_resp["choices"][0]["message"]["content"])

    async def user_prompt(self, prompt: str) -> str:
        resp = await self._request(user_prompt=prompt)
        return resp
