import json
import aiohttp
from ..types import GeneralDict, RequestDataT
import warnings


class Base:
    def __init__(
        self, api_key: str, model: str, base_endpoint: str, temperature: float = 1.0
    ) -> None:
        warnings.warn(
            "ModelSpecific classes are end to the life. Please use new gpt_models.text_generation.TextGen class instead",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self._api_key = api_key
        self._temperature = temperature
        self._model = model
        self._completions_endpoint = base_endpoint
        self._session = aiohttp.ClientSession()

    def _get_headers(self) -> GeneralDict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        return headers

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

    async def _request(
        self, data: GeneralDict | RequestDataT, method: str = "POST"
    ) -> GeneralDict:
        async with self._session.request(
            method=method,
            url=self._completions_endpoint,
            headers=self._get_headers(),
            data=json.dumps(data),
            ssl=False,
        ) as resp:
            await resp.read()

        return dict(await resp.json())
