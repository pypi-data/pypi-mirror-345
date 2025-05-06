from typing import Optional
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import GoogleCloudLogging, ClientLogger

class ClientManager:
    def __init__(
        self,
        key:str,
        name:str,
        logs_dir:str,
        service_key:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging] = None
    ) -> None:
        self._key = key
        self._name = name
        self._logs_dir = logs_dir
        self._service_key = service_key
        self._level = level
        self._google_cloud_logging = google_cloud_logging
        self._initialize_logger()
        self._logger.info("Initializing client manager")

    def _initialize_logger(self) -> None:
        self._logger = ClientLogger(
            logs_dir=self._logs_dir,
            client_key=self._key,
            service_key=self._service_key,
            level=self._level,
            google_cloud_logging=self._google_cloud_logging
        )

    @property
    def key(self) -> str:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def logger(self) -> ClientLogger:
        return self._logger

    @property
    def credentials(self):
        raise NotImplementedError()

    @property
    def client(self):
        raise NotImplementedError()