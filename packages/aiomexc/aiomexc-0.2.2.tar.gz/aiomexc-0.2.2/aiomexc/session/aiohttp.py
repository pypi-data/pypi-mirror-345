import asyncio
import ssl

from typing import Any, Dict, Type, cast
from urllib.parse import urljoin
import certifi

from aiohttp import ClientSession, TCPConnector, ClientTimeout
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE

from aiomexc.methods import MexcMethod
from aiomexc.types import MexcType
from aiomexc.__meta__ import __version__
from aiomexc import loggers
from aiomexc.retort import _retort

from .base import BaseSession, Credentials


class AiohttpSession(BaseSession):
    def __init__(self, limit: int = 100, **kwargs: Any):
        super().__init__(**kwargs)

        self._session: ClientSession | None = None
        self._connector_type: Type[TCPConnector] = TCPConnector
        self._connector_init: Dict[str, Any] = {
            "ssl": ssl.create_default_context(cafile=certifi.where()),
            "limit": limit,
            "ttl_dns_cache": 3600,  # Workaround for https://github.com/aiogram/aiogram/issues/1500
        }
        self._should_reset_connector = True  # flag determines connector state
        self._base_url = "https://api.mexc.com/api/v3/"
        self._headers = {
            "Content-Type": "application/json",
        }

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} mexc-api/{__version__}",
                },
            )
            self._should_reset_connector = False

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # Wait 250 ms for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    async def _request(
        self,
        method: MexcMethod[MexcType],
        params: dict[str, Any],
        headers: dict[str, Any],
        timeout: float | None = None,
    ) -> MexcType:
        session = await self.create_session()
        url = urljoin(self._base_url, method.__api_method__)

        loggers.client.debug(
            "Requesting %s %s with params %s", method.__api_http_method__, url, params
        )

        try:
            async with session.request(
                method.__api_http_method__,
                url,
                params=params,
                headers=headers,
                timeout=ClientTimeout(
                    total=self.timeout if timeout is None else timeout
                ),
            ) as resp:
                raw_result = await resp.json()

                if isinstance(
                    raw_result, dict
                ):  # we can trust the api that the error will not be returned in the list
                    api_code = int(raw_result.get("code", 200))
                    msg = raw_result.get("msg")
                else:
                    api_code = 200
                    msg = None

                wrapped_result = {
                    "ok": resp.ok,
                    "msg": msg,
                    "code": api_code,
                    "result": raw_result if api_code == 200 else None,
                }  # this is needed, because mexc api don't have stable response structure
        except asyncio.TimeoutError:
            raise

        loggers.client.debug("Response: %s", wrapped_result)
        response = self.check_response(method, api_code, wrapped_result)
        return cast(MexcType, response.result)

    async def make_signed_request(
        self,
        method: MexcMethod[MexcType],
        credentials: Credentials,
        timeout: float | None = None,
    ) -> MexcType:
        params = _retort.dump(method)
        headers = self._headers.copy()

        if method.__requires_auth__:
            params = self.encrypt_params(credentials.secret_key, params)
            headers["X-MEXC-APIKEY"] = credentials.access_key

        return await self._request(method, params, headers, timeout)

    async def make_request(
        self,
        method: MexcMethod[MexcType],
        timeout: float | None = None,
    ) -> MexcType:
        return await self._request(method, _retort.dump(method), self._headers, timeout)

    async def __aenter__(self) -> "AiohttpSession":
        await self.create_session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
