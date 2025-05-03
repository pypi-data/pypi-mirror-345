import os
from google.auth import default
from google.oauth2 import service_account
from maleo_foundation.managers.client.base import ClientManager

class GoogleClientManager(ClientManager):
    def __init__(self, key, name, logs_dir, google_cloud_logging=None, credentials_path=None) -> None:
        super().__init__(key, name, logs_dir, google_cloud_logging)
        credentials_path = credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        try:
            if credentials_path is not None:
                self._credentials = service_account.Credentials.from_service_account_file(filename=credentials_path)
            else:
                self._credentials, _ = default()
        except Exception as e:
            raise ValueError(f"Failed to initialize credentials: {str(e)}")

        self._project_id = self._credentials.project_id

    @property
    def credentials(self) -> service_account.Credentials:
        return self._credentials

    @property
    def project_id(self) -> str:
        return self._project_id