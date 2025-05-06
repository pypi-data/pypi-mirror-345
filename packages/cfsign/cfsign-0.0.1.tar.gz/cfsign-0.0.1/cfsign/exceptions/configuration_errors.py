from .base_cfsign_error import BaseCfSignError


class ConfigurationError(BaseCfSignError):
    pass


class ConfigurationNotSetError(ConfigurationError):
    pass
