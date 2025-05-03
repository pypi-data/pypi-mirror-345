from google.api_core import retry
from google.api_core.exceptions import NotFound
from google.cloud import secretmanager
from typing import Optional
from .base import GoogleClientManager

class GoogleSecretManager(GoogleClientManager):
    def __init__(self, logs_dir, google_cloud_logging=None, credentials_path=None) -> None:
        self._key = "google-secret-manager"
        self._name = "GoogleSecretManager"
        super().__init__(
            key=self._key,
            name=self._name,
            logs_dir=logs_dir,
            google_cloud_logging=google_cloud_logging,
            credentials_path=credentials_path
        )
        self._client = secretmanager.SecretManagerServiceClient(credentials=self._credentials)

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        return self._client

    def dispose(self) -> None:
        if self._client is not None:
            self._client = None

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