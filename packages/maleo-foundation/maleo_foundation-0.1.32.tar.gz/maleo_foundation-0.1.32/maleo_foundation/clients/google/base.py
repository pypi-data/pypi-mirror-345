import os
from google.auth import default
from google.oauth2 import service_account
from maleo_foundation.types import BaseTypes

class GoogleClientManager:
    def __init__(self, google_credentials_path:BaseTypes.OptionalString = None) -> None:
        google_credentials_path = google_credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        try:
            if google_credentials_path is not None:
                self._credentials = service_account.Credentials.from_service_account_file(filename=google_credentials_path)
            else:
                self._credentials, _ = default()
        except Exception as e:
            raise ValueError(f"Failed to initialize credentials: {str(e)}")

    @property
    def credentials(self) -> service_account.Credentials:
        return self._credentials
    
    @property
    def name(self) -> str:
        raise NotImplementedError()

    @property
    def client(self):
        raise NotImplementedError()

    def dispose(self) -> None:
        """Dispose of the client and release any resources."""
        if self._credentials is not None:
            self._credentials = None