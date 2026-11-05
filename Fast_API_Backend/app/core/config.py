from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DATABASE_URL: str | None = None
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    JWT_SECRET_KEY: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SCRYPT_ALGORITHM: Literal["scrypt"] = "scrypt"
    SCRYPT_N: int = 16384
    SCRYPT_R: int = 8
    SCRYPT_P: int = 1

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        encoded_password = quote_plus(self.DB_PASSWORD)
        return (
            f"postgresql+psycopg://{self.DB_USER}:{encoded_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
