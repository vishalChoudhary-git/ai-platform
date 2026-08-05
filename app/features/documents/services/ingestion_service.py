from uuid import UUID

# from app.core.ingestion.parsers.parser_factory import ParserFactory
from ai_document_intelligence import DocumentParser

from app.core.storage.base import StorageProvider
from app.features.documents.models.enums import DocumentStatus
from app.features.documents.repositories.document_repository import (
    DocumentRepository,
)


class IngestionService:
    """
    Handles asynchronous document processing.

    Today:
        PENDING -> PROCESSING -> READY

    Later:
        Download
        Parse
        Chunk
        Embed
    """

    def __init__(
        self,
        repository: DocumentRepository,
        storage: StorageProvider,
    ):
        self.repository = repository
        self.storage = storage

    async def set_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
    ) -> None:
        """
        Updates document processing status.
        """

        await self.repository.update_status(
            document_id,
            status,
        )

    async def process_document(
        self,
        document_id: UUID,
    ) -> None:
        document = await self.repository.get_by_id(document_id)
        await self.set_status(
            document_id,
            DocumentStatus.PROCESSING,
        )
        document = await self.repository.get_by_id(
            document_id,
        )

        if document is None:
            return

        content = await self.storage.download_document(
            document.storage_key,
        )
        parser = DocumentParser()

        parsed_document = parser.parse(
            content,
        )

        print("=" * 60)
        print(parsed_document.metadata.page_count)
        print(parsed_document.pages[0].text)
        print("=" * 60)

        await self.set_status(
            document_id,
            DocumentStatus.READY,
        )
