import logging
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Platform"
    version: str = "0.1.0"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings()


logger = logging.getLogger(__name__)

app_settings = get_settings()
