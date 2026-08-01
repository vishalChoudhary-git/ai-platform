from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.documents.models.enums import (
    DocumentStatus,
)


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    title: str

    status: DocumentStatus

    created_at: datetime
