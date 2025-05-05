import os
from google.auth import default
from google.cloud.logging import Client
from google.cloud.logging.handlers import CloudLoggingHandler
from google.oauth2 import service_account
from typing import Optional
from .base import GoogleCloudClientManager

class GoogleCloudLogging:
    _client:Optional[Client] = None

    @classmethod
    def initialize(cls) -> Client:
        """Initialize the cloud logging if not already initialized."""
        if cls._client is None:
            #* Setup credentials with fallback chain
            credentials = None
            credentials_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            try:
                if credentials_file:
                    credentials = service_account.Credentials.from_service_account_file(credentials_file)
                else:
                    credentials, _ = default()
            except Exception as e:
                raise ValueError(f"Failed to initialize credentials: {str(e)}")

            cls._client = Client(credentials=credentials)
            cls._client.setup_logging()

    @classmethod
    def dispose(cls) -> None:
        """Dispose of the cloud logging and release any resources."""
        if cls._client is not None:
            cls._client = None

    @classmethod
    def _get_client(cls) -> Client:
        """Retrieve the cloud logging client, initializing it if necessary."""
        cls.initialize()
        return cls._client

    @classmethod
    def create_handler(cls, name:str):
        cls.initialize()
        return CloudLoggingHandler(client=cls._client, name=name)

class GoogleCloudLoggingV2(GoogleCloudClientManager):
    def __init__(self, google_credentials_path = None) -> None:
        super().__init__(google_credentials_path)
        self._client = Client(credentials=self._credentials)
        self._client.setup_logging()

    @property
    def client(self) -> Client:
        return self._client

    def dispose(self) -> None:
        if self._client is not None:
            self._client = None
        return super().dispose()

    def create_handler(self, name:str) -> CloudLoggingHandler:
        return CloudLoggingHandler(client=self._client, name=name)