from typing import Any

from kombu import Queue
from pydantic import BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    # App settings
    APP_NAME: str
    APP_VERSION: str
    APP_TIMEZONE: str
    APP_PREFIX: str
    APP_SECRET_KEY: str

    # Celery settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_ENABLE_UTC = True
    CELERY_TIMEZONE: str | None = None
    CELERY_DEFAULT_QUEUE = "default"
    CELERY_QUEUES = (Queue("default"), Queue("priority_high"))
    CELERY_IMPORTS = ("app.tasks",)
    CELERY_BEAT_SCHEDULE: dict = {}

    @validator("CELERY_TIMEZONE")
    def get_celery_timezone(  # pylint: disable=no-self-argument
        cls, v: str | None, values: dict[str, Any]
    ) -> str:
        return v if isinstance(v, str) else values.get("APP_TIMEZONE")  # type: ignore

    # Jwt settings
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_DURATION: int = 60 * 24 * 8

    # Postgres settings
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str

    # Sqlalchemy settings
    SQLALCHEMY_DATABASE_URI: PostgresDsn | None = None
    SQLALCHEMY_ECHO: bool = False

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(  # pylint: disable=no-self-argument
        cls, v: str | None, values: dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),  # type: ignore
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> str | None:
        return (
            self.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")
            if self.SQLALCHEMY_DATABASE_URI
            else self.SQLALCHEMY_DATABASE_URI
        )

    # First super user settings
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_NAME: str
    FIRST_SUPERUSER_PASSWORD: str

    # User settings
    USER_OPEN_REGISTRATION: bool = False

    # Sentry
    SENTRY_DSN: HttpUrl | None = None
    SENTRY_ENVIRONMENT: str | None = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> str | None:  # pylint: disable=no-self-argument
        return v or None


settings = Settings()  # type: ignore
