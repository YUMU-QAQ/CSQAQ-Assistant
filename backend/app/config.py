"""Application configuration via pydantic-settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """App settings loaded from .env file and environment variables."""

    # CSQAQ API
    csqaq_api_token: str = ""
    csqaq_base_url: str = "https://api.csqaq.com"

    # Anthropic Claude API
    anthropic_api_key: str = ""

    # Database
    database_url: str = "sqlite+aiosqlite:///./csqaq.db"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Rate limiting
    csqaq_rate_limit: float = 1.0  # requests per second

    # Cache TTLs (seconds)
    cache_ttl_market_index: int = 60
    cache_ttl_item_search: int = 300
    cache_ttl_rankings: int = 120
    cache_ttl_charts: int = 600
    cache_ttl_cases: int = 300

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
