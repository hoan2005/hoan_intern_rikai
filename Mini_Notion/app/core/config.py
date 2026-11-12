from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = Field(default=8000, ge=1, le=65535)

    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int = Field(default=5432, ge=1, le=65535)
    db_name: str

    jwt_secret_key: SecretStr
    jwt_access_token_expire_minutes: int = Field(default=30, ge=30, le=60)
    bcrypt_algorithm: str = "bcrypt"
    bcrypt_rounds: int = Field(default=12, ge=4, le=31)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()
