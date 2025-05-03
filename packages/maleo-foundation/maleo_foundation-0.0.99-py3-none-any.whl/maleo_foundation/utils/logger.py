import logging
import os
from datetime import datetime
from typing import Callable, Optional
from maleo_foundation.clients.google.cloud.logging import GoogleCloudLoggingV2
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes

class BaseLogger(logging.Logger):
    def __init__(
        self,
        base_dir:str,
        type:BaseEnums.LoggerType,
        service_name:BaseTypes.OptionalString = None,
        client_name:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        cloud_logging_manager:Optional[GoogleCloudLoggingV2] = None
    ):
        """
        Custom extended logger with file, console, and Google Cloud Logging.

        - Logs are stored in `base_dir/logs/{type}`
        - Uses Google Cloud Logging if configured

        Args:
            base_dir (str): Base directory for logs (e.g., "/path/to/maleo_security")
            type (str): Log type (e.g., "application", "middleware")
            service_name (str): The service name (e.g., "maleo_security")
        """
        #* Ensure service_name exists
        service_name = service_name or os.getenv("SERVICE_NAME")
        if service_name is None:
            raise ValueError("SERVICE_NAME environment variable must be set if 'service_name' is set to None")

        #* Ensure client_name is valid if logger type is a client
        if type == BaseEnums.LoggerType.CLIENT and client_name is None:
            raise ValueError("'client_name' parameter must be provided if 'logger_type' is 'client'")

        self.type = type #* Define logger type

        #* Define logger name
        if self.type == BaseEnums.LoggerType.CLIENT:
            self.name = f"{service_name} - {self.type} - {client_name}"
        else:
            self.name = f"{service_name} - {self.type}"
        super().__init__(self.name, level)

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
        if cloud_logging_manager is not None:
            cloud_logging_handler = cloud_logging_manager.create_handler(name=self.name)
            self.addHandler(cloud_logging_handler)
        else:
            self.info("Cloud logging is not configured.")

        #* Define log directory
        if type == BaseEnums.LoggerType.CLIENT:
            log_dir = f"logs/{type}/{client_name}"
        else:
            log_dir = f"logs/{type}"
        full_log_dir = os.path.join(base_dir, log_dir)
        os.makedirs(full_log_dir, exist_ok=True)

        #* Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = os.path.join(full_log_dir, f"{timestamp}.log")

        #* File handler
        file_handler = logging.FileHandler(log_filename, mode="a")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

    def dispose(self):
        """Dispose of the logger by removing all handlers."""
        for handler in list(self.handlers):
            self.removeHandler(handler)
            handler.close()
        self.handlers.clear()

LoggerFactory = Callable[[], BaseLogger]