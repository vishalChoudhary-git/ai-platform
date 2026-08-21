from collections.abc import Sequence
from uuid import UUID

from redis.asyncio import Redis

from app.core.cache import get_redis
from app.core.db.session import async_session_factory
from app.core.notifications import SmtpEmailSender
from app.core.storage.cloudflare_r2 import CloudflareR2StorageProvider
from app.features.documents.repositories import DocumentRepository
from app.features.documents.repositories.document_chunk_repository import DocumentChunkRepository
from app.features.documents.services import DocumentService, IngestionService
from app.features.knowledge.services import KnowledgeService
from app.rag.factory import create_rag_service
from app.plugins.expenses.notifications import ExpenseNotificationService
from app.plugins.expenses.resolution import ExpenseResolutionService
from app.plugins.expenses.services import ExpenseService

from .service import ExpenseEvidenceProcessor


async def process_expense_documents_in_background(
    expense_id: str,
    document_ids: Sequence[UUID],
) -> None:
    async with async_session_factory() as session:
        storage = CloudflareR2StorageProvider()
        document_repository = DocumentRepository(session)
        ingestion_service = IngestionService(
            repository=document_repository,
            chunk_repository=DocumentChunkRepository(session),
            storage=storage,
        )
        redis: Redis = get_redis()
        evidence_processor = ExpenseEvidenceProcessor(
            session=session,
            ingestion_service=ingestion_service,
            redis=redis,
        )

        for document_id in document_ids:
            await evidence_processor.process(expense_id, document_id)

        document_service = DocumentService(document_repository, storage)
        expense_service = ExpenseService(session, document_service)
        knowledge_service = KnowledgeService(create_rag_service(session))
        notification_service = ExpenseNotificationService(SmtpEmailSender.from_settings())
        await ExpenseResolutionService(
            session=session,
            expense_service=expense_service,
            knowledge_service=knowledge_service,
            redis=redis,
            notification_service=notification_service,
        ).resolve(expense_id)


async def process_expense_document_in_background(
    expense_id: str,
    document_id: UUID,
) -> None:
    await process_expense_documents_in_background(expense_id, [document_id])
