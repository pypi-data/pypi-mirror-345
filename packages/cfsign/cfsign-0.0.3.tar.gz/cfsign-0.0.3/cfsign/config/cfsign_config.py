from dataclasses import dataclass
from typing import Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from cfsign.exceptions import ConfigurationNotSetError

__all__ = ("CfSignConfig",)


def _load_private_key(private_key: Union[str, bytes, rsa.RSAPrivateKey]) -> rsa.RSAPrivateKey:
    if isinstance(private_key, str):
        return serialization.load_pem_private_key(private_key.encode(), password=None, backend=default_backend())  # type: ignore
    elif isinstance(private_key, bytes):
        return serialization.load_pem_private_key(private_key, password=None, backend=default_backend())  # type: ignore
    return private_key


@dataclass(frozen=True)
class CfSignConfig:
    key_pair_id: str
    """The CloudFront Key Pair ID from AWS"""
    private_key: rsa.RSAPrivateKey
    """The private key content associated with the Key Pair ID"""

    @classmethod
    def create_config(cls, key_pair_id: str, private_key: Union[str, bytes, rsa.RSAPrivateKey]) -> "CfSignConfig":
        private_key_instance: rsa.RSAPrivateKey = _load_private_key(private_key)
        return cls(key_pair_id=key_pair_id, private_key=private_key_instance)


class GlobalConfig:
    _config: Union[CfSignConfig, None] = None

    @classmethod
    def get_config(cls) -> CfSignConfig:
        """Get the global CloudFront Signing credentials.

        Returns:
            CfSignConfig: The global CloudFront Signing credentials
        """
        if cls._config is None:
            raise ConfigurationNotSetError(
                "Global configration not set. Use `cfsign.utils.configure()` to set it or explicitly pass a configuration"
            )
        return cls._config

    @classmethod
    def set_config(cls, config: Union[CfSignConfig, None]) -> None:
        """Set the global CloudFront Signing credentials.

        Args:
            config: The configuration to set
        """
        if config is None:
            cls._config = None
        else:
            cls._config = config
