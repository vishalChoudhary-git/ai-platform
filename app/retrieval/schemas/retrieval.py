from uuid import UUID

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: int | None
    chunk_index: int
    metadata: dict
    vector_rank: int | None = None
    keyword_rank: int | None = None
    rrf_score: float | None = None
