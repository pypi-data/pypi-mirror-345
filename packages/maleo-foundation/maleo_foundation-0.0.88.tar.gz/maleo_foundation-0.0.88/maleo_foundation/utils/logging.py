import logging
import os
from datetime import datetime
from google.auth import default
from google.cloud.logging import Client
from google.cloud.logging.handlers import CloudLoggingHandler
from google.oauth2 import service_account
from typing import Optional
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes

class GoogleCloudLogging:
    def __init__(self, google_credentials_path:BaseTypes.OptionalString = None) -> None:
        google_credentials_path = google_credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        try:
            if google_credentials_path is not None:
                self._credentials = service_account.Credentials.from_service_account_file(filename=google_credentials_path)
            else:
                self._credentials, _ = default()
        except Exception as e:
            raise ValueError(f"Failed to initialize credentials: {str(e)}")
        self._client = Client(credentials=self._credentials)
        self._client.setup_logging()

    @property
    def credentials(self) -> service_account.Credentials:
        return self._credentials

    @property
    def client(self) -> Client:
        return self._client

    def dispose(self) -> None:
        if self._credentials is not None:
            self._credentials = None
        if self._client is not None:
            self._client = None

    def create_handler(self, name:str) -> CloudLoggingHandler:
        return CloudLoggingHandler(client=self._client, name=name)

class BaseLogger(logging.Logger):
    def __init__(
        self,
        logs_dir:str,
        type:BaseEnums.LoggerType,
        service_key:BaseTypes.OptionalString = None,
        client_key:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging] = None
    ):
        """
        Custom extended logger with file, console, and Google Cloud Logging.

        - Logs are stored in `logs_dir/logs/{type}`
        - Uses Google Cloud Logging if configured

        Args:
            logs_dir (str): Base directory for logs (e.g., "/path/to/service")
            type (str): Log type (e.g., "application", "middleware")
            service_key (str): The service name (e.g., "service")
        """
        self._type = type #* Declare logger type

        #* Ensure service_key exists
        self._service_key = service_key or os.getenv("SERVICE_NAME")
        if self._service_key is None:
            raise ValueError("SERVICE_NAME environment variable must be set if 'service_key' is set to None")

        self._client_key = client_key #* Declare client key

        #* Ensure client_key is valid if logger type is a client
        if self._type == BaseEnums.LoggerType.CLIENT and self._client_key is None:
            raise ValueError("'client_key' parameter must be provided if 'logger_type' is 'client'")

        #* Define logger name
        if self._type == BaseEnums.LoggerType.CLIENT:
            self._name = f"{self._service_key} - {self._type} - {self._client_key}"
        else:
            self._name = f"{self._service_key} - {self._type}"

        super().__init__(self._name, level) #* Init the superclass's logger

        #* Clear existing handlers to prevent duplicates
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()

        #* Formatter for logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        #* Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        #* Google Cloud Logging handler (If enabled)
        if google_cloud_logging is not None:
            cloud_logging_handler = google_cloud_logging.create_handler(name=self._name)
            self.addHandler(cloud_logging_handler)
        else:
            self.info("Cloud logging is not configured.")

        #* Define log directory
        if self._type == BaseEnums.LoggerType.CLIENT:
            log_dir = f"logs/{self._type}/{self._client_key}"
        else:
            log_dir = f"logs/{self._type}"
        self._log_dir = os.path.join(logs_dir, log_dir)
        os.makedirs(self._log_dir, exist_ok=True)

        #* Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(self._log_dir, f"{timestamp}.log")

        #* File handler
        file_handler = logging.FileHandler(log_filename, mode="a")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    @property
    def type(self) -> str:
        return self._type

    @property
    def service(self) -> str:
        return self._service_key

    @property
    def client(self) -> str:
        raise NotImplementedError()

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> str:
        return self._log_dir

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()

class ServiceLogger(BaseLogger):
    def __init__(
        self,
        logs_dir:str,
        type:BaseEnums.ServiceLoggerType,
        service_key:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging] = None
    ):
        super().__init__(
            logs_dir=logs_dir,
            type=type,
            service_key=service_key,
            client_key=None,
            level=level,
            google_cloud_logging=google_cloud_logging
        )

class ClientLogger(BaseLogger):
    def __init__(
        self,
        logs_dir:str,
        client_key:str,
        service_key:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging] = None
    ):
        super().__init__(
            logs_dir=logs_dir,
            type=BaseEnums.LoggerType.CLIENT,
            service_key=service_key,
            client_key=client_key,
            level=level,
            google_cloud_logging=google_cloud_logging
        )