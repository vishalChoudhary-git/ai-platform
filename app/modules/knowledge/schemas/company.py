from pydantic import ConfigDict, Field

from app.core.schemas.base import BaseSchema


class CompanyCreate(BaseSchema):
    name: str = Field(min_length=2, max_length=200)
    ticker: str = Field(min_length=2, max_length=20)
    sector: str = Field(min_length=2, max_length=200)


class CompanyResponse(BaseSchema):
    id: int
    name: str
    ticker: str
    sector: str

    model_config = ConfigDict(from_attributes=True)
