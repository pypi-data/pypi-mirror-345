from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from typing import Tuple
from maleo_foundation.authentication import Credentials, User
from maleo_foundation.models.transfers.parameters.token import BaseTokenParametersTransfers
from maleo_foundation.services.token import BaseTokenService
from maleo_foundation.utils.extractor import BaseExtractors
from maleo_foundation.utils.logging import MiddlewareLogger

class Backend(AuthenticationBackend):
    def __init__(self, logger:MiddlewareLogger, key:str):
        super().__init__()
        self._logger = logger
        self._key = key

    async def authenticate(self, conn:HTTPConnection) -> Tuple[Credentials, User]:
        client_ip = BaseExtractors.extract_client_ip(conn)
        if "Authorization" not in conn.headers:
            self._logger.info(f"Request | IP: {client_ip} | URL: {conn.url.path} - Result | General: Header did not contain authorization")
            return Credentials(), User(authenticated=False)

        auth = conn.headers["Authorization"]
        scheme, token = auth.split()
        if scheme != 'Bearer':
            self._logger.info(f"Request | IP: {client_ip} | URL: {conn.url.path} - Result | General: Authorization scheme is not Bearer")
            return Credentials(), User(authenticated=False)

        decode_token_parameters = BaseTokenParametersTransfers.Decode(key=self._key, token=token)
        decode_token_result = BaseTokenService.decode(parameters=decode_token_parameters)
        if not decode_token_result.success:
            self._logger.error(f"Request | IP: {client_ip} | URL: {conn.url.path} - Result | General: Failed decoding authorization token")
            return Credentials(token=token), User(authenticated=False)

        self._logger.info(f"Request | IP: {client_ip} | URL: {conn.url.path} - Result | Username: {decode_token_result.data.u_u} | Email: {decode_token_result.data.u_e}")
        return Credentials(token=token), User(authenticated=True, username=decode_token_result.data.u_u, email=decode_token_result.data.u_e)

def add_authentication_middleware(app:FastAPI, logger:MiddlewareLogger, key:str) -> None:
    """
    Adds Authentication middleware to the FastAPI application.

    Args:
        app: FastAPI
            The FastAPI application instance to which the middleware will be added.

        logger: MiddlewareLogger
            Authentication middleware logger to be used.

        key: str
            Public key to be used for token decoding.

    Returns:
        None: The function modifies the FastAPI app by adding Base middleware.

    Note:
        FastAPI applies middleware in reverse order of registration, so this middleware
        will execute after any middleware added subsequently.

    Example:
    ```python
    add_authentication_middleware(app=app, limit=10, window=1, cleanup_interval=60, ip_timeout=300)
    ```
    """
    app.add_middleware(AuthenticationMiddleware, backend=Backend(logger=logger, key=key))