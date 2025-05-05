import httpx
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import AsyncGenerator
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import ClientLogger
from maleo_foundation.managers.client.base import ClientManager

class URL(BaseModel):
    base:str = Field(..., "Base URL")

    @property
    def api(self) -> str:
        return f"{self.base}/api"

class HTTPClientControllerManager:
    def __init__(self, base_url:str) -> None:
        self._client = httpx.AsyncClient()
        self._url = URL(base=base_url)

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

class ClientControllerManagers(BaseModel):
    http:HTTPClientControllerManager = Field(..., description="HTTP Client Controller")

    class Config:
        arbitrary_types_allowed=True

class HTTPClientController:
    def __init__(self, manager:HTTPClientControllerManager):
        self._manager = manager

    @property
    def manager(self) -> HTTPClientControllerManager:
        return self._manager

class ClientServiceControllers(BaseModel):
    http:HTTPClientController = Field(..., description="HTTP Client Controller")

    class Config:
        arbitrary_types_allowed=True

class ClientControllers(BaseModel):
    #* Reuse this class while also adding all controllers of the client
    class Config:
        arbitrary_types_allowed=True

class ClientService:
    def __init__(self, controllers:ClientServiceControllers, logger:ClientLogger):
        self._controllers = controllers
        self._logger = logger

    @property
    def controllers(self) -> ClientServiceControllers:
        return self._controllers

    @property
    def logger(self) -> ClientLogger:
        return self._logger

class ClientServices(BaseModel):
    #* Reuse this class while also adding all the services of the client
    class Config:
        arbitrary_types_allowed=True

class MaleoClientManager(ClientManager):
    def __init__(self, key, name, logs_dir, google_cloud_logging = None, base_url:BaseTypes.OptionalString = None):
        super().__init__(key, name, logs_dir, google_cloud_logging)
        self._base_url = base_url

    def _initialize_controllers(self) -> None:
        #* Initialize managers
        http_controller_manager = HTTPClientControllerManager(base_url=self._base_url)
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