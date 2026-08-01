from uuid import UUID

from app.core.ingestion.factory import DocumentFactory
from app.core.ingestion.types import RawDocument
from app.core.utils.hashing import calculate_sha256
from app.features.documents.models.document import Document
from app.features.documents.repositories import DocumentRepository


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
    ):
        self.repository = repository

    async def ingest(
        self,
        raw_document: RawDocument,
    ) -> Document:
        checksum = calculate_sha256(raw_document.content)

        existing = await self.repository.get_by_checksum(checksum)

        if existing:
            return existing

        document = DocumentFactory.create(
            raw_document,
            checksum,
        )

        return await self.repository.create(document)

    async def create(
        self,
        document: Document,
    ) -> Document:
        return await self.repository.create(document)

    async def get_by_id(
        self,
        document_id: UUID,
    ) -> Document | None:
        return await self.repository.get_by_id(document_id)

    async def list(
        self,
    ) -> list[Document]:
        return await self.repository.list()

    async def delete(
        self,
        document: Document,
    ) -> None:
        await self.repository.delete(document)
