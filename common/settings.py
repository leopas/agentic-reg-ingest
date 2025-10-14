"""Application settings loaded from .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Google CSE
    google_api_key: str
    google_cx: str

    # OpenAI
    openai_api_key: str

    # MySQL
    mysql_host: str
    mysql_port: int = 3306
    mysql_db: str
    mysql_user: str
    mysql_password: str
    mysql_ssl_ca: str = ""

    # Application
    log_level: str = "INFO"
    request_timeout_seconds: int = 30
    ttl_days: int = 7

    # Qdrant (optional)
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "kb_regulatory"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()

