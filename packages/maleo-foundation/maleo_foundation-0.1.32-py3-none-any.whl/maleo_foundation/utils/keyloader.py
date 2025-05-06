import pathlib
from cryptography.hazmat.primitives import serialization
from typing import Optional, Union
from maleo_foundation.enums import BaseEnums

def load_key(
    type:BaseEnums.KeyType,
    path: Union[str, pathlib.Path],
    password:Optional[Union[str, bytes]] = None,
    format:BaseEnums.KeyFormatType = BaseEnums.KeyFormatType.STRING,
) -> Union[bytes, str]:
    """
    Load an RSA private or public key strictly from a file.

    Args:
        path (str | pathlib.Path): Path to the PEM file.
        password (str | bytes | None): Password for encrypted private keys (optional).

    Returns:
        rsa.RSAPrivateKey | rsa.RSAPublicKey
    """
    if not isinstance(type, BaseEnums.KeyType):
        raise TypeError("Invalid key type")

    file_path = pathlib.Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(f"Key file not found: {file_path}")

    if password is not None and not isinstance(password, (str, bytes)):
        raise TypeError("Invalid passsword type")

    if not isinstance(format, BaseEnums.KeyFormatType):
        raise TypeError("Invalid key format type")

    key_data = file_path.read_bytes()

    if type == BaseEnums.KeyType.PRIVATE:
        private_key = serialization.load_pem_private_key(
            key_data,
            password=password.encode() if isinstance(password, str) else password,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        if format == BaseEnums.KeyFormatType.BYTES:
            return private_key_bytes
        elif format == BaseEnums.KeyFormatType.STRING:
            return private_key_bytes.decode()

    elif type == BaseEnums.KeyType.PUBLIC:
        public_key = serialization.load_pem_public_key(key_data)
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        if format == BaseEnums.KeyFormatType.BYTES:
            return public_key_bytes
        elif format == BaseEnums.KeyFormatType.STRING:
            return public_key_bytes.decode()

    else:
        raise ValueError(f"Unsupported key type: {type}")