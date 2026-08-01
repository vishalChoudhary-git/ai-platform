import asyncio
from uuid import UUID

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
    ):
        self.repository = repository

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
        await self.set_status(
            document_id,
            DocumentStatus.PROCESSING,
        )

        # Temporary placeholder
        await asyncio.sleep(5)

        await self.set_status(
            document_id,
            DocumentStatus.READY,
        )
