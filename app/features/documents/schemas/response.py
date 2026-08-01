from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.documents.models.enums import (
    DocumentSource,
    DocumentStatus,
)


class DocumentResponse(BaseModel):
    """
    Standard response returned for a document.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    title: str

    file_name: str

    mime_type: str

    checksum: str

    source: DocumentSource

    status: DocumentStatus

    metadata: dict

    created_at: datetime

    updated_at: datetime


class DocumentListResponse(BaseModel):
    """
    Response returned when listing documents.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    title: str

    status: DocumentStatus

    source: DocumentSource

    created_at: datetime
