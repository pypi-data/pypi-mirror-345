from enum import StrEnum
from crypticorn.common.enums import ValidateEnumMixin


class ApiEnv(StrEnum):
    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    DOCKER = "docker"


class BaseUrl(StrEnum):
    PROD = "https://api.crypticorn.com"
    DEV = "https://api.crypticorn.dev"
    LOCAL = "http://localhost"
    DOCKER = "http://host.docker.internal"

    @classmethod
    def from_env(cls, env: ApiEnv) -> "BaseUrl":
        if env == ApiEnv.PROD:
            return cls.PROD
        elif env == ApiEnv.DEV:
            return cls.DEV
        elif env == ApiEnv.LOCAL:
            return cls.LOCAL
        elif env == ApiEnv.DOCKER:
            return cls.DOCKER


class ApiVersion(StrEnum):
    V1 = "v1"


class Service(ValidateEnumMixin, StrEnum):
    HIVE = "hive"
    KLINES = "klines"
    PAY = "pay"
    TRADE = "trade"
    AUTH = "auth"
    METRICS = "metrics"
