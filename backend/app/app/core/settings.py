from typing import Any

from kombu import Queue
from pydantic import BaseModel, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class AppSettings(BaseModel):
    NAME: str
    VERSION: str
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    PREFIX: str
    SECRET_KEY: str


class CelerySettings(BaseModel):
    BROKER_URL: str
    RESULT_BACKEND: str
    RESULT_SERIALIZER = "json"
    TASK_SERIALIZER = "json"
    ACCEPT_CONTENT = ["json"]
    ENABLE_UTC = True
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    DEFAULT_QUEUE: str = "default"
    QUEUES = (Queue("default"), Queue("priority_high"))
    IMPORTS = ("app.tasks",)
    BEAT_SCHEDULE: dict = {}


class JwtSettings(BaseModel):
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_DURATION: int = 60 * 24 * 8

    REFRESH_TOKEN_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRE_DURATION: int = 60 * 24 * 8


class PostgresSettings(BaseModel):
    HOST: str
    USER: str
    PASSWORD: str
    DB: str
    PORT: str
    DATABASE_URI: PostgresDsn | None = None

    @validator("DATABASE_URI", pre=True, always=True)
    def assemble_db_connection(  # pylint: disable=no-self-argument
        cls, v: str | None, values: dict[str, Any]
    ) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("USER"),
            password=values.get("PASSWORD"),
            host=values.get("HOST"),  # type: ignore
            port=values.get("PORT"),
            path=f"/{values.get('DB') or ''}",
        )

    @property
    def ASYNC_DATABASE_URI(self) -> str | None:
        return (
            self.DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")
            if self.DATABASE_URI
            else self.DATABASE_URI
        )


class SQLAlchemySettings(BaseModel):
    ECHO: bool = False


class FirstUserSuperSettings(BaseModel):
    EMAIL: EmailStr
    NAME: str
    PASSWORD: str


class SentrySettings(BaseModel):
    DSN: HttpUrl | None = None
    ENVIRONMENT: str | None = None

    @validator("DSN", pre=True, always=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> str | None:  # pylint: disable=no-self-argument
        return v or None


class UserSettings(BaseModel):
    OPEN_REGISTRATION: bool = False


class Settings(BaseSettings):
    APP: AppSettings
    CELERY: CelerySettings
    JWT: JwtSettings
    POSTGRES: PostgresSettings
    SQLALCHEMY: SQLAlchemySettings = SQLAlchemySettings()
    FIRST_SUPERUSER: FirstUserSuperSettings
    SENTRY: SentrySettings = SentrySettings()
    USER: UserSettings = UserSettings()

    class Config:
        case_sensitive = True
        env_nested_delimiter = "__"


settings = Settings()  # type: ignore
