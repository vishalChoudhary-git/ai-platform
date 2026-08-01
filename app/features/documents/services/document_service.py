from sqlalchemy import UUID

from app.core.ingestion.factory import DocumentFactory
from app.core.ingestion.types import RawDocument
from app.core.storage.base import StorageProvider
from app.core.utils.hashing import calculate_sha256
from app.features.documents.models.document import Document
from app.features.documents.models.enums import DocumentStatus
from app.features.documents.repositories import DocumentRepository


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage: StorageProvider,
    ):
        self.repository = repository
        self.storage = storage

    async def ingest(
        self,
        raw_document: RawDocument,
    ) -> Document:
        checksum = calculate_sha256(
            raw_document.content,
        )

        existing = await self.repository.get_by_checksum(
            checksum,
        )

        if existing:
            return existing

        stored_document = await self.storage.upload_document(
            raw_document,
        )

        document = DocumentFactory.create(
            raw_document=raw_document,
            checksum=checksum,
            storage_key=stored_document.storage_key,
        )

        return await self.repository.create(
            document,
        )

    async def process_document(
        self,
        document_id: UUID,
    ):
        await self.repository.update_status(
            document_id,
            DocumentStatus.PROCESSING,
        )

        # PDF Parsing comes later

        await self.repository.update_status(
            document_id,
            DocumentStatus.READY,
        )
