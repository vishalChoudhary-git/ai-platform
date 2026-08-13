from pydantic import BaseModel, Field


class KnowledgeQueryRequest(BaseModel):
    query: str = Field(min_length=1)
