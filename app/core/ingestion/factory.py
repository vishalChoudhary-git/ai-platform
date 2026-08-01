from app.core.ingestion.types import RawDocument
from app.features.documents.models.document import Document
from app.features.documents.models.enums import (
    DocumentStatus,
)


class DocumentFactory:
    @staticmethod
    def create(
        raw_document: RawDocument,
        checksum: str,
    ) -> Document:
        return Document(
            title=raw_document.filename,
            file_name=raw_document.filename,
            mime_type=raw_document.mime_type,
            checksum=checksum,
            source=raw_document.source,
            status=DocumentStatus.PENDING,
            metadata_=raw_document.metadata,
        )
