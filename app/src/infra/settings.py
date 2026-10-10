"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Central application configuration."""

    DATABASE_URL: str
    POSTGRES_DB: str = "vehicle_sales"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"
    DEBUG: bool = False
    VEHICLE_CORE_URL: str = "http://localhost:8081"
    VEHICLE_CORE_TIMEOUT_SECONDS: float = 5.0

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )
