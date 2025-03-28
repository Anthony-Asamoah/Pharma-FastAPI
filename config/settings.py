import os
from enum import Enum
from functools import lru_cache
from logging import INFO
from pathlib import Path
from typing import Annotated, Any

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(str, Enum):
    STAGING = "staging"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class AppSettings(BaseSettings):
    # App
    TITLE: str = "Pharma-FastAPI"
    VERSION: str = "0.1.0"
    TIMEZONE: str = "UTC"
    DESCRIPTION: str = "Pharmacy Management Software"
    IS_DEBUG: bool = False
    API_PREFIX: str = "/apis"
    DOCS_URL: str = "/docs"
    OPENAPI_URL: str = "/openapi.json"
    REDOC_URL: str = "/redoc"
    OPENAPI_PREFIX: str = ""

    # Server
    SERVER_HOST: str
    SERVER_PORT: int = 8001
    SERVER_WORKERS: int = 1
    IS_ALLOWED_CREDENTIALS: bool = True
    ALLOWED_ORIGIN_LIST: str = "*"
    ALLOWED_METHOD_LIST: list[str] = (
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
    )
    ALLOWED_HEADER_LIST: str = "*"
    LOGGING_LEVEL: int = INFO
    ACCESS_LOGGER: str = "uvicorn.access"
    ASGI_LOGGER: str = "uvicorn.asgi"
    LOGGERS: tuple[str, str] = (ASGI_LOGGER, ASGI_LOGGER)
    SECRET_KEY: Annotated[str, SecretStr]

    # Security Hashing
    HASHING_ALGORITHM_LAYER_1: str = "bcrypt"
    HASHING_ALGORITHM_LAYER_2: str = "argon2"
    HASHING_SALT: str

    # DB
    DATABASE_URL: str
    DB_POSTGRES_SCHEMA: str = "postgresql"
    DB_TIMEOUT: int = 5
    DB_POOL_SIZE: int = 100
    DB_MAX_POOL_CON: int = 80
    DB_POOL_OVERFLOW: int = 20
    IS_DB_ECHO_LOG: bool = False
    IS_DB_EXPIRE_ON_COMMIT: bool = False
    IS_DB_FORCE_ROLLBACK: bool = True
    # File Storage
    BASE_DIR: Any = Path(__file__).resolve().parent.parent

    UPLOAD_URL: str = "/uploads/"
    UPLOAD_ROOT: str = os.path.join(BASE_DIR, 'uploads')
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR.parent, ".env"),
        case_sensitive=True,
        validate_assignment=True,
        extra="allow",
    )

    # jwt
    ACCESS_TOKEN_EXPIRES_IN: int = 60
    REFRESH_TOKEN_EXPIRES_IN: int = 60 * 24
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "7b6c506ee07337cc3d02536d5119c4b2"
    JWT_PRIVATE_KEY: str = "sec31d048faecfc812b7835718dac4dd74eac8e3eet"
    JWT_PUBLIC_KEY: str = "faecfc812b7835718dac4dd74ea"
    JWT_REFRESH_KEY: str = "048faeba7203f5fdda"

    intruder_list: list = []

    @property
    def set_app_attributes(self) -> dict[str, str | bool | None]:
        """
        Set all `FastAPI` class' attributes with the custom values defined in `BackendBaseSettings`.
        """
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.IS_DEBUG,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
            "openapi_prefix": self.OPENAPI_PREFIX,
            "api_prefix": self.API_PREFIX,
        }


class AppStagingSettings(AppSettings):
    ENVIRONMENT: AppEnvironment = AppEnvironment.STAGING
    DESCRIPTION: str = f"Application ({ENVIRONMENT})."
    IS_DEBUG: bool = True


class AppDevelopmentSettings(AppSettings):
    ENVIRONMENT: AppEnvironment = AppEnvironment.DEVELOPMENT
    DESCRIPTION: str = f"Application ({ENVIRONMENT})."
    IS_DEBUG: bool = True


class AppProductionSettings(AppSettings):
    ENVIRONMENT: AppEnvironment = AppEnvironment.PRODUCTION
    DESCRIPTION: str = f"Application ({ENVIRONMENT})."


class FactoryAppSettings:
    def __init__(self, environment: str):
        self.environment = environment

    def __call__(self) -> AppSettings:
        if self.environment == AppEnvironment.PRODUCTION:
            return AppProductionSettings()
        elif self.environment == AppEnvironment.STAGING:
            return AppStagingSettings()
        return AppDevelopmentSettings()


@lru_cache()
def get_settings() -> AppSettings:
    return FactoryAppSettings(environment="APP_ENV")()


settings = get_settings()
