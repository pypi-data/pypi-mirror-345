"""
Implements a ClientSession which is also capable of caching response payload data to a backend.
"""
import contextlib
import logging
from http.client import InvalidURL
from typing import Self, Unpack

from aiohttp import ClientSession, ClientRequest
from aiohttp.payload import JsonPayload

from aiorequestful._utils import format_url_log
from aiorequestful.cache.backend.base import ResponseCache, ResponseRepository
from aiorequestful.cache.response import CachedResponse
from aiorequestful.types import RequestKwargs

ClientSession.__init_subclass__ = lambda *_, **__: _  # WORKAROUND: forces disabling of inheritance warning


class CachedSession(ClientSession):
    """
    A modified session which attempts to get/save responses from/to a stored cache before/after sending it.

    :param cache: The cache to use for managing cached responses.
    """

    __slots__ = ("cache",)

    def __init__(self, cache: ResponseCache, **kwargs):
        super().__init__(**kwargs)

        #: The :py:class:`logging.Logger` for this  object
        self.logger: logging.Logger = logging.getLogger(__name__)

        #: The cache to use when attempting to return a cached response.
        self.cache = cache

    async def __aenter__(self) -> Self:
        self.cache = await self.cache.__aenter__()
        await super().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self.cache.__aexit__(exc_type, exc_val, exc_tb)

    @contextlib.asynccontextmanager
    async def request(self, persist: bool = True, **kwargs: Unpack[RequestKwargs]):
        """
        Perform HTTP request.

        Arguments passed through to `.aiohttp.ClientSession.request`.
        See aiohttp reference for more info on available kwargs:
        https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession.request

        :param persist: Whether to persist responses returned from sending network requests i.e. non-cached responses.
        :return: Either the :py:class:`CachedResponse` if a response was found in the cache,
            or the :py:class:`ClientResponse` if the request was sent.
        """
        url = kwargs["url"]
        try:
            kwargs["url"] = self._build_url(url)
        except ValueError as exc:
            raise InvalidURL(url) from exc

        kwargs["headers"] = kwargs.get("headers", {}) | dict(self.headers)
        if (json_data := kwargs.pop("json", None)) is not None:
            kwargs["data"] = JsonPayload(json_data, dumps=self._json_serialize)

        drop_kwargs = ("allow_redirects",)

        req = ClientRequest(
            loop=self._loop,
            response_class=self._response_class,
            session=self,
            trust_env=self.trust_env,
            **{k: v for k, v in kwargs.items() if k not in drop_kwargs},
        )

        repository = self.cache.get_repository_from_requests(req.request_info)
        response = await self._get_cached_response(req, repository=repository)
        self._log_cache_hit(request=req, response=response)
        if response is None:
            response = await super().request(**kwargs)

        yield response

        if persist and repository is not None and response.ok and not isinstance(response, CachedResponse):
            await repository.save_response(response)

    async def _get_cached_response(
            self, request: ClientRequest, repository: ResponseRepository | None
    ) -> CachedResponse | None:
        if repository is None:
            return

        payload = await repository.get_response(request)
        if payload is None:
            return

        if not isinstance(payload, str | bytes):
            repository = self.cache.get_repository_from_url(request.url)
            payload = await repository.serialize(payload)

        return CachedResponse(request=request, payload=payload)

    def _log_cache_hit(self, request: ClientRequest, response: CachedResponse | None) -> None:
        message = "CACHE HIT" if isinstance(response, CachedResponse) else "HTTP REQUEST"
        self.logger.debug(format_url_log(method="CACHE", url=request.url, messages=message))
