import json
import os
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.types import Lifespan, AppType
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from sqlalchemy import MetaData
from typing import Optional, Type
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.transfers.general.token import BaseTokenGeneralTransfers
from maleo_foundation.models.transfers.parameters.token import BaseTokenParametersTransfers
from maleo_foundation.managers.client.google.secret import GoogleSecretManager
from maleo_foundation.managers.client.google.storage import GoogleCloudStorage
from maleo_foundation.managers.client.http import HTTPClientManager
from maleo_foundation.managers.client.maleo import MaleoClientManager
from maleo_foundation.managers.db import DatabaseManager
from maleo_foundation.managers.middleware import MiddlewareConfigurations, MiddlewareLoggers, MiddlewareManager
from maleo_foundation.middlewares.base import RequestProcessor
from maleo_foundation.services.token import BaseTokenService
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.exceptions import BaseExceptions
from maleo_foundation.utils.keyloader import load_key
from maleo_foundation.utils.logging import GoogleCloudLogging, ServiceLogger, MiddlewareLogger

class LogConfig(BaseModel):
    logs_dir:str = Field(..., description="Logs directory")
    google_cloud_logging:GoogleCloudLogging = Field(..., description="Google cloud's logging")

    class Config:
        arbitrary_types_allowed=True

class Settings(BaseSettings):
    ENVIRONMENT:BaseEnums.EnvironmentType = Field(..., description="Environment")
    GOOGLE_CREDENTIALS_PATH:str = Field("/creds/maleo-google-service-account.json", description="Internal credential's file path")
    INTERNAL_CREDENTIALS_PATH:str = Field("/creds/maleo-internal-service-account.json", description="Internal credential's file path")
    PRIVATE_KEY_PATH:str = Field("/keys/maleo-private-key.pem", description="Maleo's private key path")
    PUBLIC_KEY_PATH:str = Field("/keys/maleo-public-key.pem", description="Maleo's public key path")
    KEY_PASSWORD:str = Field(..., description="Maleo key's password")
    CONFIGURATIONS_PATH:str = Field(..., description="Service's configuration file path")
    GCS_BUCKET_NAME:str = Field(..., description="Google cloud storage (GCS)'s bucket name")

class Keys(BaseModel):
    password:str = Field(..., description="Key's password")
    private:str = Field(..., description="Private key")
    public:str = Field(..., description="Public key")

class GoogleCredentials(BaseModel):
    type:str = Field(..., description="Credentials type")
    project_id:str = Field(..., description="Google project ID")
    private_key_id:str = Field(..., description="Private key ID")
    private_key:str = Field(..., description="Private key")
    client_email:str = Field(..., description="Client email")
    client_id:str = Field(..., description="Client ID")
    auth_uri:str = Field(..., description="Authorization URI")
    token_uri:str = Field(..., description="Token URI")
    auth_provider_x509_cert_url:str = Field(..., description="Authorization provider x509 certificate URL")
    client_x509_cert_url:str = Field(..., description="Client x509 certificate URL")
    universe_domain:str = Field(..., description="Universe domains")

class InternalCredentials(BaseModel):
    system_role:str = Field(..., description="System role")
    username:str = Field(..., description="Username")
    email:str = Field(..., description="Email")
    user_type:str = Field(..., description="User type")

class Credentials(BaseModel):
    google:GoogleCredentials = Field(..., description="Google's credentials")
    internal:InternalCredentials = Field(..., description="Internal's credentials")

    class Config:
        arbitrary_types_allowed=True

class ServiceConfigurations(BaseModel):
    key:str = Field(..., description="Service's key")
    name:str = Field(..., description="Service's name")
    host:str = Field(..., description="Service's host")
    port:int = Field(..., description="Service's port")

class DatabaseConfigurations(BaseModel):
    username:str = Field("postgres", description="Database user's username")
    password:str = Field(..., description="Database user's password")
    host:str = Field(..., description="Database's host")
    port:int = Field(5432, description="Database's port")
    database:str = Field(..., description="Database")

    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class MaleoClientConfiguration(BaseModel):
    key:str = Field(..., description="Client's key")
    name:str = Field(..., description="Client's name")
    url:str = Field(..., description="Client's URL")

class MaleoClientConfigurations(BaseModel):
    metadata:MaleoClientConfiguration = Field(..., description="MaleoMetadata client's configuration")
    security:MaleoClientConfiguration = Field(..., description="MaleoSecurity client's configuration")
    storage:MaleoClientConfiguration = Field(..., description="MaleoStorage client's configuration")
    identity:MaleoClientConfiguration = Field(..., description="MaleoIdentity client's configuration")
    access:MaleoClientConfiguration = Field(..., description="MaleoAccess client's configuration")
    soapie:MaleoClientConfiguration = Field(..., description="MaleoSOAPIE client's configuration")
    fhir:MaleoClientConfiguration = Field(..., description="MaleoFHIR client's configuration")
    dicom:MaleoClientConfiguration = Field(..., description="MaleoDICOM client's configuration")
    scribe:MaleoClientConfiguration = Field(..., description="MaleoScribe client's configuration")
    cds:MaleoClientConfiguration = Field(..., description="MaleoCDS client's configuration")
    imaging:MaleoClientConfiguration = Field(..., description="MaleoImaging client's configuration")
    mcu:MaleoClientConfiguration = Field(..., description="MaleoMCU client's configuration")

    class Config:
        arbitrary_types_allowed=True

class ClientConfigurations(BaseModel):
    maleo:MaleoClientConfigurations = Field(..., description="Maleo client's configurations")

class Configurations(BaseModel):
    service:ServiceConfigurations = Field(..., description="Service's configurations")
    middleware:MiddlewareConfigurations = Field(..., description="Middleware's configurations")
    database:DatabaseConfigurations = Field(..., description="Database's configurations")
    client:ClientConfigurations = Field(..., description="Service's configurations")

    class Config:
        arbitrary_types_allowed=True

class Loggers(BaseModel):
    application:ServiceLogger = Field(..., description="Application logger")
    database:ServiceLogger = Field(..., description="Database logger")
    middleware:MiddlewareLoggers = Field(..., description="Middleware logger")

    class Config:
        arbitrary_types_allowed=True

class GoogleClientManagers(BaseModel):
    secret:GoogleSecretManager = Field(..., description="Google secret manager client manager")
    storage:GoogleCloudStorage = Field(..., description="Google cloud storage client manager")

    class Config:
        arbitrary_types_allowed=True

class MaleoClientManagerClasses(BaseModel):
    metadata:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoMetadata client manager")
    security:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoSecurity client manager")
    storage:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoStorage client manager")
    identity:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoIdentity client manager")
    access:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoAccess client manager")
    soapie:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoSOAPIE client manager")
    fhir:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoFHIR client manager")
    dicom:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoDICOM client manager")
    scribe:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoScribe client manager")
    cds:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoCDS client manager")
    imaging:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoImaging client manager")
    mcu:Optional[Type[MaleoClientManager]] = Field(None, description="MaleoMCU client manager")

    class Config:
        arbitrary_types_allowed=True

class MaleoClientManagers(BaseModel):
    metadata:Optional[MaleoClientManager] = Field(None, description="MaleoMetadata client manager")
    security:Optional[MaleoClientManager] = Field(None, description="MaleoSecurity client manager")
    storage:Optional[MaleoClientManager] = Field(None, description="MaleoStorage client manager")
    identity:Optional[MaleoClientManager] = Field(None, description="MaleoIdentity client manager")
    access:Optional[MaleoClientManager] = Field(None, description="MaleoAccess client manager")
    soapie:Optional[MaleoClientManager] = Field(None, description="MaleoSOAPIE client manager")
    fhir:Optional[MaleoClientManager] = Field(None, description="MaleoFHIR client manager")
    dicom:Optional[MaleoClientManager] = Field(None, description="MaleoDICOM client manager")
    scribe:Optional[MaleoClientManager] = Field(None, description="MaleoScribe client manager")
    cds:Optional[MaleoClientManager] = Field(None, description="MaleoCDS client manager")
    imaging:Optional[MaleoClientManager] = Field(None, description="MaleoImaging client manager")
    mcu:Optional[MaleoClientManager] = Field(None, description="MaleoMCU client manager")

    class Config:
        arbitrary_types_allowed=True

class ClientManagers(BaseModel):
    google:GoogleClientManagers = Field(..., description="Google client's managers")
    http:Type[HTTPClientManager] = Field(..., description="HTTP client's manager")
    maleo:MaleoClientManagers = Field(..., description="Maleo client's managers")

    class Config:
        arbitrary_types_allowed=True

class ServiceManager:
    def __init__(
        self,
        db_metadata:MetaData,
        base_dir:BaseTypes.OptionalString = None,
        settings:Optional[Settings] = None,
        google_cloud_logging:Optional[GoogleCloudLogging] = None,
        maleo_client_manager_classes:Optional[MaleoClientManagerClasses] = None
    ):
        self._db_metadata = db_metadata

        if base_dir is None:
            self._base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
        else:
            self._base_dir = base_dir

        self._logs_dir = os.path.join(self._base_dir, "logs")

        #* Initialize settings
        if settings is None:
            self._settings = Settings()
        else:
            self._settings = settings

        #* Load configs
        self._load_configs()

        #* Initialize google cloud logging
        if google_cloud_logging is None:
            self._google_cloud_logging = GoogleCloudLogging()
        else:
            self._google_cloud_logging = google_cloud_logging

        self._log_config = LogConfig(
            logs_dir=self._logs_dir,
            google_cloud_logging=self._google_cloud_logging
        )

        self._initialize_loggers()
        self._load_credentials()
        self._parse_keys()
        self._initialize_db()

        #* Initialize maleo client managers
        if maleo_client_manager_classes is None:
            self._maleo_client_manager_classes = MaleoClientManagerClasses()
        else:
            self._maleo_client_manager_classes = maleo_client_manager_classes
        self._initialize_clients()

    @property
    def base_dir(self) -> str:
        return self._base_dir

    @property
    def logs_dir(self) -> str:
        return self._logs_dir
    
    @property
    def log_config(self) -> LogConfig:
        return self._log_config

    @property
    def settings(self) -> Settings:
        return self._settings

    def _load_configs(self) -> None:
        with open(self._settings.CONFIGURATIONS_PATH) as f:
            data = json.load(f)
            self._configs = Configurations.model_validate(data)

    @property
    def configs(self) -> Configurations:
        return self._configs

    def _initialize_loggers(self) -> None:
        #* Service's loggers
        application = ServiceLogger(type=BaseEnums.LoggerType.APPLICATION, service_key=self._configs.service.key, **self._log_config.model_dump())
        database = ServiceLogger(type=BaseEnums.LoggerType.DATABASE, service_key=self._configs.service.key, **self._log_config.model_dump())
        #* Middleware's loggers
        base = MiddlewareLogger(middleware_type=BaseEnums.MiddlewareLoggerType.BASE, service_key=self._configs.service.key, **self._log_config.model_dump())
        authentication = MiddlewareLogger(middleware_type=BaseEnums.MiddlewareLoggerType.AUTHENTICATION, service_key=self._configs.service.key, **self._log_config.model_dump())
        middleware = MiddlewareLoggers(base=base, authentication=authentication)
        self._loggers = Loggers(application=application, database=database, middleware=middleware)

    @property
    def loggers(self) -> Loggers:
        return self._loggers

    def _load_credentials(self) -> None:
        #* Load google credentials
        with open(self._settings.GOOGLE_CREDENTIALS_PATH) as f:
            data = json.load(f)
            google = GoogleCredentials.model_validate(data)
        #* Load internal credentials
        with open(self._settings.INTERNAL_CREDENTIALS_PATH) as f:
            data = json.load(f)
            internal = InternalCredentials.model_validate(data)
        self._credentials = Credentials(google=google, internal=internal)

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    def _parse_keys(self) -> None:
        #* Parse private key
        key_type = BaseEnums.KeyType.PRIVATE
        private = load_key(
            type=key_type,
            path=self._settings.PRIVATE_KEY_PATH,
            password=self._settings.KEY_PASSWORD
        )
        #* Parse public key
        key_type = BaseEnums.KeyType.PUBLIC
        public = load_key(
            type=key_type,
            path=self._settings.PUBLIC_KEY_PATH
        )
        self._keys = Keys(password=self._settings.KEY_PASSWORD, private=private, public=public)

    @property
    def keys(self) -> Keys:
        return self._keys

    def _initialize_db(self) -> None:
        self._database = DatabaseManager(metadata=self._db_metadata, logger=self._loggers.database, url=self._configs.database.url)

    @property
    def database(self) -> DatabaseManager:
        return self._database

    def _initialize_clients(self) -> None:
        #* Initialize google clients
        secret = GoogleSecretManager(**self._log_config.model_dump())
        storage = GoogleCloudStorage(**self._log_config.model_dump())
        self._google_clients = GoogleClientManagers(secret=secret, storage=storage)
        #* Initialize http clients
        self._http_client = HTTPClientManager
        self._http_client.initialize()
        #* Initialize maleo clients
        self._maleo_clients = MaleoClientManagers()
        for client in self._maleo_client_manager_classes.__class__.__annotations__:
            client_cls = getattr(self._maleo_client_manager_classes, client)
            if client_cls is not None and issubclass(client_cls, MaleoClientManager):
                cfg:MaleoClientConfiguration = getattr(self._configs.client.maleo, client)
                client_instance = client_cls(**cfg.model_dump(), **self._log_config.model_dump())
                setattr(self._maleo_clients, client, client_instance)
        self._clients = ClientManagers(google=self._google_clients, http=self._http_client, maleo=self._maleo_clients)

    @property
    def google_clients(self) -> GoogleClientManagers:
        return self._google_clients

    @property
    def http_client(self) -> Type[HTTPClientManager]:
        return self._http_client

    @property
    def maleo_clients(self) -> MaleoClientManagers:
        return self._maleo_clients

    @property
    def clients(self) -> ClientManagers:
        return self._clients

    @property
    def token(self) -> str:
        payload = BaseTokenGeneralTransfers.BaseEncodePayload(
            sr=self._credentials.internal.system_role,
            u_u=self._credentials.internal.username,
            u_e=self._credentials.internal.email,
            u_ut=self._credentials.internal.user_type
        )
        parameters = BaseTokenParametersTransfers.Encode(
            key=self.keys.private,
            password=self.keys.password,
            payload=payload
        )
        result = BaseTokenService.encode(parameters=parameters)
        if not result.success:
            raise ValueError("Failed generating token")
        return result.data.token

    def create_app(self, router:APIRouter, lifespan:Optional[Lifespan[AppType]] = None, request_processor:Optional[RequestProcessor] = None) -> FastAPI:
        self._loggers.application.info("Creating FastAPI application")
        self._app = FastAPI(title=self._configs.service.name, lifespan=lifespan)
        self._loggers.application.info("FastAPI application created successfully")

        #* Add middleware(s)
        self._loggers.application.info("Configuring middlewares")
        self._middleware = MiddlewareManager(app=self._app, configurations=self._configs.middleware)
        self._middleware.add_all(loggers=self.loggers.middleware, key=self._keys.public, request_processor=request_processor)
        self._loggers.application.info("Middlewares addedd successfully")

        #* Add exception handler(s)
        self._loggers.application.info("Adding exception handlers")
        self._app.add_exception_handler(RequestValidationError, BaseExceptions.validation_exception_handler)
        self._app.add_exception_handler(HTTPException, BaseExceptions.http_exception_handler)
        self._loggers.application.info("Exception handlers addedd successfully")

        #* Include router
        self._loggers.application.info("Including routers")
        self._app.include_router(router)
        self._loggers.application.info("Routers included successfully")

        return self._app

    @property
    def app(self) -> FastAPI:
        return self._app

    async def dispose(self) -> None:
        self._loggers.application.info("Disposing service manager")
        if self._database is not None:
            self._database.dispose()
            self._database = None
        if self._clients is not None:
            self._clients.google.storage.dispose()
            self._clients.google.secret.dispose()
            await self._clients.http.dispose()
            for client in self._maleo_clients.__class__.__annotations__:
                client_instance = getattr(self._maleo_clients, client)
                if client_instance is not None and isinstance(client_instance, MaleoClientManager):
                    await client_instance.dispose()
        self._loggers.application.info("Service manager disposed successfully")
        if self._loggers is not None:
            self._loggers.application.info("Disposing logger")
            self._loggers.application.dispose()
            self._loggers.database.info("Disposing logger")
            self._loggers.database.dispose()
            self._loggers.middleware.base.info("Disposing logger")
            self._loggers.middleware.base.dispose()
            self._loggers.middleware.authentication.info("Disposing logger")
            self._loggers.middleware.authentication.dispose()
            self._loggers = None