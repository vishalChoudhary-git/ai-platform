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
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_platform"
    r2_account_id: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str
    r2_endpoint_url: str
    llama_cloud_api_key: str
    tier: str
    openai_api_key: str
    openrouter_api_key: str
    openrouter_site_url: str = "https://github.com/vishalChoudhary-git/ai-platform"
    openrouter_site_name: str = "AI Platform"
    openrouter_reranker_model: str = "nvidia/llama-nemotron-rerank-vl-1b-v2:free"
    rag_llm_model: str = "gpt-4.1-mini"
    rag_llm_max_tokens: int
    rag_llm_temperature: float


@lru_cache
def get_settings() -> Settings:
    return Settings()


logger = logging.getLogger(__name__)

app_settings = get_settings()
