from google.api_core import retry
from google.api_core.exceptions import NotFound
from google.cloud import secretmanager
from typing import Optional
from .base import GoogleClientManager

class GoogleSecretManager(GoogleClientManager):
    def __init__(self, google_credentials_path = None) -> None:
        super().__init__(google_credentials_path)
        self._project_id = self.credentials.project_id
        self._client = secretmanager.SecretManagerServiceClient(credentials=self.credentials)

    @property
    def project_id(self):
        return self._project_id

    @property
    def client(self) -> secretmanager.SecretManagerServiceClient:
        return self._client

    def dispose(self):
        if self._client is not None:
            self._client = None
        return super().dispose()

    @retry.Retry(predicate=retry.if_exception_type(Exception), timeout=5)
    def get(self, name:str, version:str = "latest") -> Optional[str]:
        try:
            secret_path = f"projects/{self._project_id}/secrets/{name}/versions/{version}"
            request = secretmanager.AccessSecretVersionRequest(name=secret_path)
            response = self._client.access_secret_version(request=request)
            return response.payload.data.decode()
        except Exception as e:
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