from typing import Optional
from maleo_foundation.utils.logging import GoogleCloudLogging, ClientLogger

class ClientManager:
    def __init__(self, key:str, name:str, logs_dir:str, google_cloud_logging:Optional[GoogleCloudLogging] = None) -> None:
        self._key = key
        self._name = name
        self._logs_dir = logs_dir
        self._google_cloud_logging = google_cloud_logging
        self._initialize_logger()

    def _initialize_logger(self) -> None:
        self._logger = ClientLogger(logs_dir=self._logs_dir, client_key=self._key, google_cloud_logging=self._google_cloud_logging)

    @property
    def key(self) -> str:
        return self._key

    @property
    def name(self) -> str:
        return self._name

    @property
    def logger(self):
        return self._logger

    @property
    def credentials(self):
        raise NotImplementedError()

    @property
    def client(self):
        raise NotImplementedError()