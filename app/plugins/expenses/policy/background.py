from sqlalchemy import select

from app.core.cache import get_redis
from app.core.db.session import async_session_factory
from app.core.storage.cloudflare_r2 import CloudflareR2StorageProvider
from app.features.documents.repositories import DocumentRepository
from app.features.documents.repositories.document_chunk_repository import DocumentChunkRepository
from app.features.documents.services import IngestionService

from .cache import ExpensePolicyCache
from .models import ExpensePolicy
from .processor import ExpensePolicyProcessor


async def process_policy_in_background(policy_id: str) -> None:
    async with async_session_factory() as session:
        policy = await session.scalar(
            select(ExpensePolicy).where(ExpensePolicy.policy_id == policy_id)
        )
        if policy is None:
            raise ValueError(f"Expense policy '{policy_id}' was not found.")

        ingestion_service = IngestionService(
            repository=DocumentRepository(session),
            chunk_repository=DocumentChunkRepository(session),
            storage=CloudflareR2StorageProvider(),
        )
        await ingestion_service.process_document(policy.document_id)

        await ExpensePolicyProcessor(
            session=session,
            cache=ExpensePolicyCache(get_redis()),
        ).process(policy_id)
