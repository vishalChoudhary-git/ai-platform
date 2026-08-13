from ai_document_intelligence.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import app_settings
from app.retrieval.openrouter_nemotron_reranker import OpenRouterNemotronReranker
from app.retrieval.repositories import RetrievalRepository
from app.retrieval.reranking import Reranker
from app.retrieval.services import RetrievalService


def create_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider(
        api_key=app_settings.openai_api_key,
    )


def create_reranker() -> Reranker:
    return OpenRouterNemotronReranker(
        api_key=app_settings.openrouter_api_key,
        model=app_settings.openrouter_reranker_model,
        site_url=app_settings.openrouter_site_url,
        site_name=app_settings.openrouter_site_name,
    )


def create_retrieval_service(
    session: AsyncSession,
) -> RetrievalService:
    return RetrievalService(
        repository=RetrievalRepository(session),
        embedding_provider=create_embedding_provider(),
        reranker=create_reranker(),
    )
