from pydantic import Field

from app.schemas.base import BaseSchema


class PaginationParams(BaseSchema):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=1, ge=1, le=100)


class PaginatedResponse(BaseSchema):
    items: list
    page: int
    size: int
    total: int
