import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import AsyncGenerator
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import ClientLogger
from maleo_foundation.managers.client.base import ClientManager

class URL(BaseModel):
    base:str = Field(..., description="Base URL")

    @property
    def api(self) -> str:
        return f"{self.base}/api"

class ClientHTTPControllerManager:
    def __init__(self, url:str) -> None:
        self._client = httpx.AsyncClient()
        self._url = URL(base=url)

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
        return self._url

    async def dispose(self) -> None:
        await self._client.aclose()

class ClientControllerManagers(BaseModel):
    http:ClientHTTPControllerManager = Field(..., description="HTTP Client Controller")

    class Config:
        arbitrary_types_allowed=True

class ClientHTTPController:
    def __init__(self, manager:ClientHTTPControllerManager):
        self._manager = manager

    @property
    def manager(self) -> ClientHTTPControllerManager:
        return self._manager

class ClientServiceControllers(BaseModel):
    http:ClientHTTPController = Field(..., description="HTTP Client Controller")

    class Config:
        arbitrary_types_allowed=True

class ClientControllers(BaseModel):
    #* Reuse this class while also adding all controllers of the client
    class Config:
        arbitrary_types_allowed=True

class ClientService:
    def __init__(self, logger:ClientLogger):
        self._logger = logger

    @property
    def controllers(self) -> ClientServiceControllers:
        raise NotImplementedError()

    @property
    def logger(self) -> ClientLogger:
        return self._logger

class ClientServices(BaseModel):
    #* Reuse this class while also adding all the services of the client
    class Config:
        arbitrary_types_allowed=True

class MaleoClientManager(ClientManager):
    def __init__(self, key, name, logs_dir, google_cloud_logging = None, url:BaseTypes.OptionalString = None):
        super().__init__(key, name, logs_dir, google_cloud_logging)
        self._url = url

    def _initialize_controllers(self) -> None:
        #* Initialize managers
        http_controller_manager = ClientHTTPControllerManager(url=self._url)
        self._controller_managers = ClientControllerManagers(http=http_controller_manager)
        #* Initialize controllers
        #! This initialied an empty controllers. Extend this function in the actual class to initialize all controllers.
        self._controllers = ClientControllers()

    @property
    def controllers(self) -> ClientControllers:
        raise self._controllers

    def _initialize_services(self) -> None:
        #* Initialize services
        #! This initialied an empty services. Extend this function in the actual class to initialize all services.
        self._services = ClientServices()

    @property
    def services(self) -> ClientServices:
        return self._services

    async def dispose(self) -> None:
        self._logger.info("Disposing client manager")
        await self._controller_managers.http.dispose()
        self._logger.info("Client manager disposed successfully")