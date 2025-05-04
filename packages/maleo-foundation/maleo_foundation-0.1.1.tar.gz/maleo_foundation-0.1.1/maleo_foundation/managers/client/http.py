import httpx
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

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
    async def dispose(cls) -> None:
        """Dispose of the HTTP client and release any resources."""
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None