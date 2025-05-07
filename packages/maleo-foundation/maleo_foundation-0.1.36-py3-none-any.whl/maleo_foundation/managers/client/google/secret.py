from google.api_core import retry
from google.api_core.exceptions import NotFound
from google.cloud import secretmanager
from typing import Optional
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes
from maleo_foundation.utils.logging import GoogleCloudLogging
from .base import GoogleClientManager

class GoogleSecretManager(GoogleClientManager):
    def __init__(
        self,
        logs_dir:str,
        service_key:BaseTypes.OptionalString = None,
        level:BaseEnums.LoggerLevel = BaseEnums.LoggerLevel.INFO,
        google_cloud_logging:Optional[GoogleCloudLogging] = None,
        credentials_path:BaseTypes.OptionalString=None
    ) -> None:
        key = "google-secret-manager"
        name = "GoogleSecretManager"
        super().__init__(
            key=key,
            name=name,
            logs_dir=logs_dir,
            service_key=service_key,
            level=level,
            google_cloud_logging=google_cloud_logging,
            credentials_path=credentials_path
        )
        self._client = secretmanager.SecretManagerServiceClient(credentials=self._credentials)
        self._logger.info("Client manager initialized successfully")

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        return self._client

    def dispose(self) -> None:
        if self._client is not None:
            self._logger.info("Disposing client manager")
            self._client = None
            self._logger.info("Client manager disposed successfully")

    @retry.Retry(predicate=retry.if_exception_type(Exception), timeout=5)
    def get(self, name:str, version:str = "latest") -> Optional[str]:
        try:
            secret_path = f"projects/{self._project_id}/secrets/{name}/versions/{version}"
            request = secretmanager.AccessSecretVersionRequest(name=secret_path)
            response = self._client.access_secret_version(request=request)
            self._logger.info("Successfully retrieved secret '%s' with version '%s'", name, version)
            return response.payload.data.decode()
        except Exception:
            self._logger.error("Exception occured with retrieving secret '%s' with version '%s'", name, version, exc_info=True)
            return None

    @retry.Retry(predicate=retry.if_exception_type(Exception), timeout=5)
    def create(self, name:str, data:str) -> Optional[str]:
        parent = f"projects/{self._project_id}"
        secret_path = f"{parent}/secrets/{name}"
        try:
            #* Check if the secret already exists
            request = secretmanager.GetSecretRequest(name=secret_path)
            self._client.get_secret(request=request)

        except NotFound:
            #* Secret does not exist, create it first
            try:
                secret = secretmanager.Secret(name=name, replication={"automatic": {}})
                request = secretmanager.CreateSecretRequest(parent=parent, secret_id=name, secret=secret)
                self._client.create_secret(request=request)
            except Exception as e:
                return None

        #* Add a new secret version
        try:
            payload = secretmanager.SecretPayload(data=data.encode())
            request = secretmanager.AddSecretVersionRequest(parent=secret_path, payload=payload)
            response = self._client.add_secret_version(request=request)
            return data
        except Exception as e:
            return None