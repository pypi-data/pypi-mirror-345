"""
Configuration module based on tiangolo implementation of `pydantic_settings`.
Custom implementation by Artemis Resende <artemis@aresende.com>

Source: https://github.com/fastapi/full-stack-fastapi-template/blob/d2020c1a37efd368afee4d3e56897fc846614f80/backend/app/core/config.py
Licensed under MIT
"""
import logging
from pathlib import Path
from typing import Optional, Any

from commons.database import DatabaseAdapter
from commons.locales import LocaleSettings
from commons.network import IPV4_LOOPBACK
from fastapi_mail import ConnectionConfig
from pydantic import computed_field, model_validator, EmailStr, SecretStr, PrivateAttr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from webserver import env


# noinspection PyNestedDecorators
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{env.root()}/.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_NAME: str = "fastapi.webserver"
    ENVIRONMENT: env.Environment = "local"
    RESOURCES_FOLDER: Path | str = env.root()
    MODULES: list[str] | str = []              # string list separated by commas
    TEMPLATES_FOLDER: str = ""                 # Enables HTML support for templating; Should be relative to RESOURCES_PATH and not start with a '/'
    WORKERS: int = 4

    # --- LOGGING ---
    LOG_LEVEL: int | str = logging.INFO
    LOG_DIR: Optional[Path | str] = None
    LOG_FILE_MAX_BYTES: int = 1024 * 1024  # 1MB
    LOG_FILE_BACKUP_MAX_COUNT: int = 5
    LOG_FORMAT: str = "%(asctime)s.%(msecs)03d - %(name)s [%(levelname)s]: %(message)s"
    LOG_DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"  # ISO 8601
    LOG_USE_COLORS: bool = True

    # --- HTTP  ---
    HTTP_ROOT_PATH: str = '/'                  # it must start with a '/'
    STATIC_FOLDER: str = ""                    # Enables `{HTTP_ROOT_PATH}/static`; Should be relative to RESOURCES_PATH and not start with a '/'
    HOST: str = IPV4_LOOPBACK
    PORT: int = 8000
    ENABLE_SSL: bool = False
    SSL_CERTIFICATE: str = ""
    SSL_PRIVATE_KEY: str = ""
    CORS_ORIGINS: list[str] = []  # string list separated by commas

    # --- I18n ---
    _locale_config: Optional[LocaleSettings] = PrivateAttr(default=None)
    SUPPORTED_LOCALES: list[str] | str = []

    # --- Database ---
    _database_adapter: Optional[DatabaseAdapter]  = PrivateAttr(default=None)
    _cache_database_adapter: DatabaseAdapter  = PrivateAttr(default=None)
    DB_ENGINE: str = ""
    DB_SERVER: str = ""
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = ""

    # --- SMTP ---
    _smtp_config: Optional[ConnectionConfig] = PrivateAttr(default=None)
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[SecretStr] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # --- Keys ---
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8         # 60 minutes * 24 hours * 8 days = 8 days

    @computed_field
    @property
    def resources_folder(self) -> Path:
        return Path(self.RESOURCES_FOLDER)

    @computed_field
    @property
    def base_url(self) -> str:
        import re
        def is_ip_address(s):
            # Regex to check if the string is an IPv4 address
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if re.match(ipv4_pattern, s):
                # Check if each octet is between 0 and 255
                octets = s.split('.')
                for octet in octets:
                    if not (0 <= int(octet) <= 255):
                        return False
                return True
            return False

        schema: str = "https" if self.enable_ssl else "http"
        base_url: str
        if is_ip_address(self.HOST) or self.HOST == "localhost":
            base_url = f"{schema}://{self.HOST}:{self.PORT}{self.HTTP_ROOT_PATH}"
        else:
            base_url = f"{schema}://{self.HOST}{self.HTTP_ROOT_PATH}"

        return base_url

    @computed_field
    @property
    def enable_ssl(self) -> bool:
        return bool(self.SSL_CERTIFICATE and self.SSL_PRIVATE_KEY) or self.ENABLE_SSL

    @computed_field
    @property
    def http_static_enabled(self) -> bool:
        return bool(self.RESOURCES_FOLDER and self.STATIC_FOLDER)

    @computed_field
    @property
    def static_folder(self) -> Optional[Path]:
        if self.http_static_enabled:
            return Path(f"{self.RESOURCES_FOLDER}/{self.STATIC_FOLDER}")

    @computed_field
    @property
    def ssl_certificate(self) -> Optional[Path]:
        if self.SSL_CERTIFICATE:
            return Path(self.SSL_CERTIFICATE)

    @computed_field
    @property
    def ssl_private_key(self) -> Optional[Path]:
        if self.SSL_PRIVATE_KEY:
            return Path(self.SSL_PRIVATE_KEY)

    @computed_field
    @property
    def templates_enabled(self) -> bool:
        return bool(self.RESOURCES_FOLDER and self.TEMPLATES_FOLDER)

    @computed_field
    @property
    def templates_folder(self) -> Optional[Path]:
        if self.templates_enabled:
            return Path(f"{self.RESOURCES_FOLDER}/{self.TEMPLATES_FOLDER}")

    @computed_field
    @property
    def locale_config(self) -> Optional[LocaleSettings]:
        if self.SUPPORTED_LOCALES and not self._locale_config:
            self._locale_config = LocaleSettings(
                translations_directory=self.resources_folder / "translations",
                supported_locales=self.SUPPORTED_LOCALES
            )

        return self._locale_config

    @computed_field
    @property
    def has_database(self) -> bool:
        return bool(self.DB_ENGINE and self.DB_NAME)

    @computed_field
    @property
    def database_adapter(self) -> Optional[DatabaseAdapter]:
        if self.has_database and not self._database_adapter:
            self._database_adapter = DatabaseAdapter(
                scheme=self.DB_ENGINE,
                host=self.DB_SERVER,
                port=self.DB_PORT,
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                database=f"{self.RESOURCES_FOLDER}/{self.DB_NAME}" if self.DB_ENGINE.startswith(
                    "sqlite") else self.DB_NAME
            )

        return self._database_adapter

    @computed_field
    @property
    def cache_database_adapter(self) -> DatabaseAdapter:
        if self.resources_folder and not self._cache_database_adapter:
            self._cache_database_adapter = DatabaseAdapter(
                scheme="sqlite",
                database=f"{self.resources_folder}/cache.db"
            )

        return self._cache_database_adapter

    @computed_field
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL and self.SMTP_USER and self.SMTP_PASSWORD)

    @computed_field
    @property
    def smtp_config(self) -> Optional[ConnectionConfig]:
        if self.emails_enabled and (not self._smtp_config):
            # build SMTP Config
            args: dict = {
                "MAIL_USERNAME": self.SMTP_USER,
                "MAIL_PASSWORD": self.SMTP_PASSWORD,
                "MAIL_FROM": self.EMAILS_FROM_EMAIL,
                "MAIL_PORT": self.SMTP_PORT,
                "MAIL_SERVER": self.SMTP_HOST,
                "MAIL_FROM_NAME": self.EMAILS_FROM_NAME,
                "MAIL_STARTTLS": True,
                "MAIL_SSL_TLS": False,
                "USE_CREDENTIALS": True,
            }

            if self.templates_enabled:
                args["TEMPLATE_FOLDER"] = self.templates_folder

            self._smtp_config = ConnectionConfig(**args)

        return self._smtp_config

    @computed_field
    @property
    def uvicorn_logging_config(self) -> dict[str, Any]:
        """
        Convert the settings into an Uvicorn-compatible logging configuration dictionary.

        :return: A dictionary compatible with Uvicorn's logging configuration.
        """
        uvicorn_logging_config: dict[str, Any] = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": self.LOG_FORMAT,
                    "datefmt": self.LOG_DATETIME_FORMAT,
                    "use_colors": True,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": self.LOG_FORMAT,
                    "datefmt": self.LOG_DATETIME_FORMAT,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": self.LOG_LEVEL, "propagate": False},
                "uvicorn.error": {"level": self.LOG_LEVEL},
                "uvicorn.access": {"handlers": ["access"], "level": self.LOG_LEVEL, "propagate": False},
            },
        }

        # If a log directory is specified, add file handlers
        if self.LOG_DIR:
            log_dir = Path(self.LOG_DIR)
            if not log_dir.exists():
                log_dir.mkdir(exist_ok=True, parents=True)

            # Add file handler for default logs
            uvicorn_logging_config["handlers"]["file_default"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_dir / f"{self.APP_NAME}.log"),
                "formatter": "default",
                "maxBytes": self.LOG_FILE_MAX_BYTES,
                "backupCount": self.LOG_FILE_BACKUP_MAX_COUNT,
            }

            # Add file handler for access logs
            uvicorn_logging_config["handlers"]["file_access"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_dir / f"{self.APP_NAME}_access.log"),
                "formatter": "access",
                "maxBytes": self.LOG_FILE_MAX_BYTES,
                "backupCount": self.LOG_FILE_BACKUP_MAX_COUNT,
            }

            # Update loggers to use file handlers
            uvicorn_logging_config["loggers"]["uvicorn"]["handlers"].append("file_default")
            uvicorn_logging_config["loggers"]["uvicorn.access"]["handlers"].append("file_access")

        return uvicorn_logging_config

    # --- VALIDATORS ---

    @field_validator("RESOURCES_FOLDER", mode="before")
    @classmethod  # classmethod annotation should be declared after the field validator annotation to make it work
    def validate_required_path(cls, v: str):
        if Path(v).exists():
            return v

        raise ValueError(f"'{v}' does not exists.")

    @field_validator("LOG_LEVEL", mode="before")
    @classmethod
    def validate_log_level(cls, level: str | int) -> int:
        """
        Parse the log level string.
        :param level: a string describing the log level, or the int representation of the level
        :return: an int representation of the log level
        """
        import logging
        if isinstance(level, str):
            level = level.strip().lower()
            match level:
                case "info":
                    return logging.INFO
                case "debug":
                    return logging.DEBUG
                case "warn":
                    return logging.WARNING
                case "warning":
                    return logging.WARNING
                case "error":
                    return logging.ERROR
                case "fatal":
                    return logging.ERROR
                case _:
                    raise ValueError("Log level is invalid.")
        elif isinstance(level, int):
            if 0 <= level <= 50:
                return int(level)
            else:
                raise ValueError(
                    "Log level must be between 0 and 50. See https://docs.python.org/3/library/logging.html#logging-levels")
        else:
            return logging.NOTSET

    @field_validator("CORS_ORIGINS", "SUPPORTED_LOCALES", "MODULES", mode="before")
    @classmethod
    def validate_string_list(cls, v: str):
        """
        Parse a string list of elements separated by commas.
        :param v:
        :return: a comma-separated list
        """
        if isinstance(v, str):
            if not v.startswith("["):
                return [i.strip() for i in v.split(",")]
            else:
                return [v]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    @field_validator("SSL_CERTIFICATE", "SSL_PRIVATE_KEY")
    @classmethod
    def validate_optional_path(cls, v: str):
        if not v or Path(v).exists():
            return v

        raise ValueError(f"'{v}' does not exists.")

    @model_validator(mode="after")
    def _post_construct_hook(self) -> Self:
        from commons import logging

        logging.config(level=self.LOG_LEVEL,
                       directory=self.LOG_DIR,
                       format=self.LOG_FORMAT,
                       datefmt=self.LOG_DATETIME_FORMAT,
                       max_file_bytes=self.LOG_FILE_MAX_BYTES,
                       backup_count=self.LOG_FILE_BACKUP_MAX_COUNT)

        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.APP_NAME

        return self


# ------
settings: Settings = Settings()
