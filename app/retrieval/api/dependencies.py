from ai_document_intelligence.embeddings import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import app_settings
from app.core.db.session import get_db
from app.retrieval.repositories import RetrievalRepository
from app.retrieval.services import RetrievalService


def get_retrieval_repository(
    session: AsyncSession = Depends(get_db),
) -> RetrievalRepository:
    return RetrievalRepository(session)


def get_embedding_provider() -> EmbeddingProvider:
    return OpenAIEmbeddingProvider(
        api_key=app_settings.openai_api_key,
    )


def get_retrieval_service(
    repository: RetrievalRepository = Depends(
        get_retrieval_repository,
    ),
    embedding_provider: EmbeddingProvider = Depends(
        get_embedding_provider,
    ),
) -> RetrievalService:
    return RetrievalService(
        repository=repository,
        embedding_provider=embedding_provider,
    )
