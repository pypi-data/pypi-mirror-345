from .logging import GoogleCloudLogging
from .secret import GoogleSecretManager
from .storage import GoogleCloudStorage

class GoogleCloudClients:
    Logging = GoogleCloudLogging
    Secret = GoogleSecretManager
    Storage = GoogleCloudStorage