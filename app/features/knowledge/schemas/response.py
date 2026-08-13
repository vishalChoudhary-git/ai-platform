from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeSource(BaseModel):
    source_index: int = Field(ge=1)
    chunk_id: UUID
    document_id: UUID
    page_number: int | None
    chunk_index: int
    text: str


class KnowledgeQueryResponse(BaseModel):
    answer: str
    sources: list[KnowledgeSource]
