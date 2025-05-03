import json
import time
import hmac
import hashlib

from urllib.parse import urlencode
from abc import ABC, abstractmethod
from typing import Callable, Any, Final, cast
from dataclasses import dataclass

from http import HTTPStatus
from aiomexc.methods import MexcMethod
from aiomexc.types import MexcResult, MexcType
from aiomexc.exceptions import (
    MexcBadRequest,
    MexcNotFound,
    MexcApiKeyInvalid,
    MexcApiKeyMissing,
    MexcAPIError,
    MexcApiInvalidListenKey,
)
from aiomexc.retort import _retort

_JsonLoads = Callable[..., Any]
_JsonDumps = Callable[..., str]
DEFAULT_TIMEOUT: Final[float] = 60.0


@dataclass
class Credentials:
    access_key: str
    secret_key: str


class BaseSession(ABC):
    def __init__(
        self,
        json_loads: _JsonLoads = json.loads,
        json_dumps: _JsonDumps = json.dumps,
        timeout: float = DEFAULT_TIMEOUT,
        recv_window: int = 30000,
    ):
        self.json_loads = json_loads
        self.json_dumps = json_dumps
        self.timeout = timeout
        self.recv_window = recv_window

        self._map_error_code_to_exception = {
            700004: MexcBadRequest,  # Param 'origClientOrderId' or 'orderId' must be sent, but both were empty/null
            400: MexcBadRequest,  # api key required
            -1121: MexcBadRequest,  # Invalid symbol
            -2013: MexcNotFound,  # Order does not exist
            10072: MexcApiKeyInvalid,  # Invalid API-Key format
            402: MexcApiKeyMissing,  # API-Key missing, not sure
            730708: MexcApiInvalidListenKey,  # Invalid listen key
        }

    def encrypt_params(self, secret_key: str, params: dict | None = None) -> dict:
        """
        Encrypt params for auth required requests

        :param secret_key: Secret key
        :param params: Params to encrypt
        :return: Encrypted params
        """
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}
        else:
            params = {}

        params["recvWindow"] = self.recv_window
        params["timestamp"] = int(time.time() * 1000)  # timestamp in milliseconds

        encoded_params = urlencode(params)
        params["signature"] = hmac.new(
            secret_key.encode(), encoded_params.encode(), hashlib.sha256
        ).hexdigest()
        return params

    def check_response(
        self, method: MexcMethod[MexcType], status_code: int, json_data: dict
    ) -> MexcResult[MexcType]:
        response_type = MexcResult[method.__returning__]
        response = _retort.load(json_data, response_type)

        if HTTPStatus.OK <= status_code <= HTTPStatus.IM_USED and response.ok:
            return response

        message = cast(str, response.msg)

        if exception_cls := self._map_error_code_to_exception.get(status_code):
            raise exception_cls(
                method=method,
                message=message,
            )

        raise MexcAPIError(
            method=method,
            message=message,
        )

    @abstractmethod
    async def make_signed_request(
        self,
        method: MexcMethod[MexcType],
        credentials: Credentials,
        timeout: float | None = None,
    ) -> MexcType:  # pragma: no cover
        """
        Make signed request to Mexc API

        :param method: Method instance
        :param credentials: Credentials instance
        :param timeout: Request timeout
        :return:
        :raise MexcAPIError:
        """
        pass

    @abstractmethod
    async def make_request(
        self,
        method: MexcMethod[MexcType],
        timeout: float | None = None,
    ) -> MexcType:  # pragma: no cover
        """
        Make request to Mexc API

        :param method: Method instance
        :param timeout: Request timeout
        :param credentials: Optional credentials to use for this specific request
        :return:
        :raise MexcAPIError:
        """
        pass

    @abstractmethod
    async def close(self) -> None:  # pragma: no cover
        """
        Close client session
        """
        pass
