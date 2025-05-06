from starlette.authentication import (
    AuthCredentials,
    BaseUser
)
from typing import Optional, Sequence

class Credentials(AuthCredentials):
    def __init__(
        self,
        token:Optional[str] = None,
        scopes:Optional[Sequence[str]] = None
    ) -> None:
        self.token = token
        super().__init__(scopes)

class User(BaseUser):
    def __init__(
        self,
        authenticated:bool = True,
        username:str = "",
        email:str = ""
    ) -> None:
        self._authenticated = authenticated
        self._username = username
        self._email = email

    @property
    def is_authenticated(self) -> bool:
        return self._authenticated

    @property
    def display_name(self) -> str:
        return self._username

    @property
    def identity(self) -> str:
        return self._email