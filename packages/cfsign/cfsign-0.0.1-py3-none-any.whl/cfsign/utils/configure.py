from typing import Union

from cryptography.hazmat.primitives.asymmetric import rsa

from cfsign.config.cfsign_config import CfSignConfig, GlobalConfig

__all__ = ("configure",)


def configure(key_pair_id: str, private_key: Union[str, bytes, rsa.RSAPrivateKey]) -> None:
    """Configure the global CloudFront Signing credentials.

    Args:
        cf_key_pair_id: The CloudFront Key Pair ID from AWS
        private_key: The private key content associated with the Key Pair ID

    Returns:
        None
    """
    GlobalConfig.set_config(CfSignConfig.create_config(key_pair_id, private_key))
