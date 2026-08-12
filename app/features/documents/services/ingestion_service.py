from uuid import UUID, uuid4

# from app.core.ingestion.parsers.parser_factory import ParserFactory
from ai_document_intelligence import DocumentProcessor
from ai_document_intelligence.chunking import MarkdownChunker
from ai_document_intelligence.embeddings import OpenAIEmbeddingProvider
from ai_document_intelligence.parsers import LlamaParseParser

from app.core.config import app_settings
from app.core.storage.base import StorageProvider
from app.features.documents.models.document_chunk import DocumentChunk
from app.features.documents.models.enums import DocumentStatus
from app.features.documents.repositories.document_chunk_repository import DocumentChunkRepository
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
        chunk_repository: DocumentChunkRepository,
        storage: StorageProvider,
    ):
        self.repository = repository
        self.chunk_repository = chunk_repository
        self.storage = storage
        self.parser = LlamaParseParser(
            api_key=app_settings.llama_cloud_api_key,
            tier="cost_effective",
            version="latest",
        )
        self.embedding_provider = OpenAIEmbeddingProvider(
            api_key=app_settings.openai_api_key,
        )
        self.chunker = MarkdownChunker(
            max_characters=2000,
        )
        self.processor = DocumentProcessor(
            parser=self.parser,
            chunker=self.chunker,
            embedding_provider=self.embedding_provider,
        )

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

    # async def process_document(
    #     self,
    #     document_id: UUID,
    # ) -> None:

    #     document = await self.repository.get_by_id(
    #         document_id,
    #     )

    #     if document is None:
    #         return

    #     await self.set_status(
    #         document_id,
    #         DocumentStatus.PROCESSING,
    #     )

    #     try:
    #         content = await self.storage.download_document(
    #             document.storage_key,
    #         )
    #         print(f"document========{document.id}")
    #         processed_document = self.processor.process(
    #             content,
    #             document_id="258c2805-fad7-46f1-80c8-3f854251d1b5",
    #         )

    #         chunks = []

    #         for embedded_chunk in processed_document.embedded_chunks:
    #             chunk = embedded_chunk.chunk

    #             chunks.append(
    #                 DocumentChunk(
    #                     id=UUID(chunk.id)
    #                     if isinstance(chunk.id, str)
    #                     else chunk.id,
    #                     document_id=chunk.document_id,
    #                     text=chunk.text,
    #                     page_number=chunk.page_number,
    #                     chunk_index=chunk.chunk_index,
    #                     metadata=chunk.metadata,
    #                     embedding=embedded_chunk.embedding,
    #                 )
    #             )
    #         # await self.chunk_repository.create_many(
    #         #     chunks,
    #         # )

    #         await self.set_status(
    #             document_id,
    #             DocumentStatus.READY,
    #         )

    #     except Exception:
    #         await self.set_status(
    #             document_id,
    #             DocumentStatus.FAILED,
    #         )

    #         raise

    async def process_document(
        self,
        document_id: UUID,
    ) -> None:
        document = await self.repository.get_by_id(
            document_id,
        )

        if document is None:
            return

        await self.set_status(
            document_id,
            DocumentStatus.PROCESSING,
        )

        try:
            content = await self.storage.download_document(
                document.storage_key,
            )

            processed_document = self.processor.process(
                content,
                document_id=str(document_id),
            )

            chunks: list[DocumentChunk] = []

            for embedded_chunk in processed_document.embedded_chunks:
                chunk = embedded_chunk.chunk
                print(f"chunk id ===={chunk.id}")
                chunk_metadata = {
                    **chunk.metadata,
                    "sdk_chunk_id": chunk.id,
                }

                chunks.append(
                    DocumentChunk(
                        id=uuid4(),
                        document_id=chunk.document_id,
                        text=chunk.text,
                        page_number=chunk.page_number,
                        chunk_index=chunk.chunk_index,
                        embedding=embedded_chunk.embedding,
                        metadata_=chunk_metadata,
                    )
                )

            await self.chunk_repository.create_many(
                chunks,
            )

            await self.set_status(
                document_id,
                DocumentStatus.READY,
            )

        except Exception:
            await self.set_status(
                document_id,
                DocumentStatus.FAILED,
            )

            raise
