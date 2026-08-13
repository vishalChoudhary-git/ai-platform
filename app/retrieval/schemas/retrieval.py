from uuid import UUID

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: int | None
    chunk_index: int
    metadata: dict
    similarity: float


class RetrievalResponse(BaseModel):
    results: list[RetrievedChunk]
