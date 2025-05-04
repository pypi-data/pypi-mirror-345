import httpx
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

class HTTPClientManager:
    client:Optional[httpx.AsyncClient] = None
    base_url:Optional[str] = None

    @classmethod
    def initialize(cls) -> None:
        """Initialize the HTTP client if not already initialized."""
        if cls.client is None:
            cls.client = httpx.AsyncClient()

    @classmethod
    async def _client_handler(cls) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Reusable generator for client handling."""
        if cls.client is None:
            raise RuntimeError("Client has not been initialized. Call initialize first.")

        yield cls.client

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
    def get_url(cls) -> str:
        if cls.base_url is None:
            raise RuntimeError("Base URL has not been initialized. Call initialize first.")
        return cls.base_url

    @classmethod
    async def dispose(cls) -> None:
        """Dispose of the HTTP client and release any resources."""
        if cls.client is not None:
            await cls.client.aclose()
            cls.client = None
        if cls.base_url is not None:
            cls.base_url = None