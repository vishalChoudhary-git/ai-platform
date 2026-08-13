from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    min_similarity: float = Field(default=0.3, ge=0.0, le=1.0)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be empty")
        return value


class KeywordSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be empty")
        return value


class RetrievedChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: int | None
    chunk_index: int
    metadata: dict
    similarity: float


class KeywordSearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    text: str
    page_number: int | None
    chunk_index: int
    metadata: dict
    score: float


class RetrievalResponse(BaseModel):
    results: list[RetrievedChunk]


class KeywordSearchResponse(BaseModel):
    results: list[KeywordSearchResult]
