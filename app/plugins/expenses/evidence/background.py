from app.core.cache import get_redis
from app.core.db.session import async_session_factory
from app.core.storage.cloudflare_r2 import CloudflareR2StorageProvider
from app.features.documents.repositories import DocumentRepository
from app.features.documents.repositories.document_chunk_repository import DocumentChunkRepository
from app.features.documents.services import IngestionService

from .service import ExpenseEvidenceProcessor


async def process_expense_document_in_background(
    expense_id: str,
    document_id,
) -> None:
    async with async_session_factory() as session:
        ingestion_service = IngestionService(
            repository=DocumentRepository(session),
            chunk_repository=DocumentChunkRepository(session),
            storage=CloudflareR2StorageProvider(),
        )
        await ExpenseEvidenceProcessor(
            session=session,
            ingestion_service=ingestion_service,
            redis=get_redis(),
        ).process(expense_id, document_id)
