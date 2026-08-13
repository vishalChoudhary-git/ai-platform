import os

from ai_document_intelligence.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import app_settings
from app.retrieval.openrouter_nemotron_reranker import OpenRouterNemotronReranker
from app.retrieval.reranking import Reranker
from app.retrieval.repositories import RetrievalRepository
from app.retrieval.services import RetrievalService


def create_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider(
        api_key=app_settings.openai_api_key,
    )


def create_reranker() -> Reranker:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required")

    return OpenRouterNemotronReranker(
        api_key=api_key,
        model=os.getenv(
            "OPENROUTER_RERANKER_MODEL",
            "nvidia/llama-nemotron-rerank-vl-1b-v2:free",
        ),
        site_url=os.getenv(
            "OPENROUTER_SITE_URL",
            "https://github.com/vishalChoudhary-git/ai-platform",
        ),
        site_name=os.getenv(
            "OPENROUTER_SITE_NAME",
            "AI Platform",
        ),
    )


def create_retrieval_service(
    session: AsyncSession,
) -> RetrievalService:
    return RetrievalService(
        repository=RetrievalRepository(session),
        embedding_provider=create_embedding_provider(),
        reranker=create_reranker(),
    )
