import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import AsyncGenerator, Optional
from maleo_foundation.managers.client.base import ClientManager

class HTTPClientManager:
    _client:Optional[httpx.AsyncClient] = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize the HTTP client if not already initialized."""
        if cls._client is None:
            cls._client = httpx.AsyncClient()

    @classmethod
    async def _client_handler(cls) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Reusable generator for client handling."""
        if cls._client is None:
            raise RuntimeError("Client has not been initialized. Call initialize first.")
        yield cls._client

    @classmethod
    async def inject_client(cls) -> AsyncGenerator[httpx.AsyncClient, None]:
        return cls._client_handler()

    @classmethod
    @asynccontextmanager
    async def get_client(cls) -> AsyncGenerator[httpx.AsyncClient, None]:
        """
        Async context manager for manual HTTP client handling.
        Supports `async with HTTPClientManager.get() as client:`
        """
        async for client in cls._client_handler():
            yield client

    @classmethod
    def get_base_url(cls) -> str:
        raise NotImplementedError()

    @classmethod
    async def dispose(cls) -> None:
        """Dispose of the HTTP client and release any resources."""
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None

class URL(BaseModel):
    base:str = Field(..., description="Base URL")

    @property
    def api(self) -> str:
        return f"{self.base}/api"

class HTTPClientManagerV2(ClientManager):
    def __init__(self, key, name, logs_dir, google_cloud_logging = None):
        super().__init__(key, name, logs_dir, google_cloud_logging)
        self._client = httpx.AsyncClient()

    async def _client_handler(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Reusable generator for client handling."""
        yield self._client

    async def inject_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        return self._client_handler()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """
        Async context manager for manual HTTP client handling.
        Supports `async with HTTPClientManager.get() as client:`
        """
        async for client in self._client_handler():
            yield client

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client

    @property
    def url(self) -> URL:
        raise NotImplementedError()