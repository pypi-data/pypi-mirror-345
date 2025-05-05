from typing import Dict
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logger import BaseLogger

class ClientLoggerManager:
    _loggers:Dict[type, BaseLogger] = {}

    @classmethod
    def initialize(
        cls,
        base_dir:str,
        client_name:str,
        service_name:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO
    ) -> BaseLogger:
        """Initialize client logger if not already initialized."""
        if cls not in cls._loggers:
            cls._loggers[cls] = BaseLogger(
                base_dir=base_dir,
                type=BaseEnums.LoggerType.CLIENT,
                service_name=service_name,
                client_name=client_name,
                level=level
            )
        return cls._loggers[cls]

    @classmethod
    def get(cls) -> BaseLogger:
        """Return client logger (if exist) or raise Runtime Error"""
        if cls not in cls._loggers:
            raise RuntimeError("Logger has not been initialized. Call 'initialize' first.")
        return cls._loggers[cls]

class MaleoFoundationLoggerManager(ClientLoggerManager):
    @classmethod
    def initialize(
        cls,
        base_dir:str,
        service_name:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO
    ) -> BaseLogger:
        """Initialize MaleoFoundation's client logger if not already initialized."""
        return super().initialize(
            base_dir=base_dir,
            client_name="MaleoFoundation",
            service_name=service_name,
            level=level
        )

    @classmethod
    def get(cls) -> BaseLogger:
        """Return client logger (if exist) or raise Runtime Error"""
        return super().get()