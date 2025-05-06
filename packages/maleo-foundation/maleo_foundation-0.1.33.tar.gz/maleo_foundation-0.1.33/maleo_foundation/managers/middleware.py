from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from maleo_foundation.middlewares.authentication import add_authentication_middleware
from maleo_foundation.middlewares.base import add_base_middleware, RequestProcessor
from maleo_foundation.middlewares.cors import add_cors_middleware
from maleo_foundation.utils.logging import MiddlewareLogger

_ALLOW_METHODS:List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
_ALLOW_HEADERS:List[str] = ["X-Organization", "X-User", "X-Signature"]
_EXPOSE_HEADERS:List[str] = ["X-Request-Timestamp", "X-Response-Timestamp", "X-Process-Time", "X-Signature"]

class GeneralMiddlewareConfigurations(BaseModel):
    allow_origins:List[str] = Field(default_factory=list, description="Allowed origins")
    allow_methods:List[str] = Field(_ALLOW_METHODS, description="Allowed methods")
    allow_headers:list[str] = Field(_ALLOW_HEADERS, description="Allowed headers")
    allow_credentials:bool = Field(False, description="Allowed credentials")

class CORSMiddlewareConfigurations(BaseModel):
    expose_headers:List[str] = Field(_EXPOSE_HEADERS, description="Exposed headers")

class BaseMiddlewareConfigurations(BaseModel):
    limit:int = Field(10, description="Request limit (per 'window' seconds)")
    window:int = Field(1, description="Request limit window (seconds)")
    cleanup_interval:int = Field(60, description="Interval for middleware cleanup (seconds)")
    ip_timeout:int = Field(300, description="Idle IP's timeout (seconds)")

class MiddlewareConfigurations(BaseModel):
    general:GeneralMiddlewareConfigurations = Field(..., description="Middleware's general configurations")
    cors:CORSMiddlewareConfigurations = Field(..., description="CORS middleware's configurations")
    base:BaseMiddlewareConfigurations = Field(..., description="Base middleware's configurations")

class MiddlewareLoggers(BaseModel):
    base:MiddlewareLogger = Field(..., description="Base middleware's logger")
    authentication:MiddlewareLogger = Field(..., description="Authentication middleware's logger")

    class Config:
        arbitrary_types_allowed=True

class MiddlewareManager:
    def __init__(self, app:FastAPI, configurations:MiddlewareConfigurations):
        self._app = app
        self._configurations = configurations

    def add_all(
        self,
        loggers:MiddlewareLoggers,
        key:str,
        request_processor:Optional[RequestProcessor] = None
    ):
        self.add_cors()
        self.add_base(logger=loggers.base, request_processor=request_processor)
        self.add_authentication(logger=loggers.authentication, key=key)

    def add_cors(self) -> None:
        add_cors_middleware(
            app=self._app,
            allow_origins=self._configurations.general.allow_origins,
            allow_methods=self._configurations.general.allow_methods,
            allow_headers=self._configurations.general.allow_headers,
            allow_credentials=self._configurations.general.allow_credentials,
            expose_headers=self._configurations.cors.expose_headers
        )

    def add_base(self, logger:MiddlewareLogger, request_processor:Optional[RequestProcessor] = None):
        add_base_middleware(
            app=self._app,
            logger=logger,
            allow_origins=self._configurations.general.allow_origins,
            allow_methods=self._configurations.general.allow_methods,
            allow_headers=self._configurations.general.allow_headers,
            allow_credentials=self._configurations.general.allow_credentials,
            limit=self._configurations.base.limit,
            window=self._configurations.base.window,
            cleanup_interval=self._configurations.base.cleanup_interval,
            ip_timeout=self._configurations.base.ip_timeout,
            request_processor=request_processor
        )

    def add_authentication(self, logger:MiddlewareLogger, key:str):
        add_authentication_middleware(app=self._app, logger=logger, key=key)