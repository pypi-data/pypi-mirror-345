import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import cfsign
from cfsign.config.cfsign_config import CfSignConfig, GlobalConfig
from cfsign.exceptions.configuration_errors import ConfigurationNotSetError


def test_not_configured() -> None:
    with pytest.raises(ConfigurationNotSetError):
        GlobalConfig.get_config()


def test_global_config_set_and_get(config: CfSignConfig) -> None:
    GlobalConfig.set_config(config)
    assert GlobalConfig.get_config() is config


def test_global_config_set_and_get_none() -> None:
    GlobalConfig.set_config(None)
    with pytest.raises(ConfigurationNotSetError):
        GlobalConfig.get_config()


def test_configure_alias(config: CfSignConfig) -> None:
    cfsign.configure(config.key_pair_id, config.private_key)
    assert GlobalConfig.get_config() == config
    assert GlobalConfig.get_config() is not config


def test_configure_alias_none() -> None:
    cfsign.configure(None, None)  # type: ignore
    assert GlobalConfig.get_config() == CfSignConfig(key_pair_id=None, private_key=None)  # type: ignore


def test_load_private_key_all_formats(private_key: rsa.RSAPrivateKey) -> None:
    key_pair_id = "test"

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_key_str = private_key_bytes.decode()
    private_key_rsa = private_key

    cfsign.configure(key_pair_id, private_key_bytes)
    assert (
        GlobalConfig.get_config().private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        == private_key_bytes
    )

    cfsign.configure(key_pair_id, private_key_str)
    assert (
        GlobalConfig.get_config().private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        == private_key_bytes
    )

    cfsign.configure(key_pair_id, private_key_rsa)
    assert GlobalConfig.get_config().private_key == private_key_rsa
