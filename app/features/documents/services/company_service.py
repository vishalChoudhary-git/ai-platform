from fastapi import HTTPException, status

from app.features.documents.models.company import Company
from app.features.documents.repositories.company_repository import CompanyRepository
from app.features.documents.schemas.company import CompanyCreate


class CompanyService:
    def __init__(
        self,
        repository: CompanyRepository,
    ):
        self.repository = repository

    async def get_all(
        self,
        page: int,
        size: int,
        sector: str | None,
    ):
        return await self.repository.get_all(page, size, sector)

    async def create(self, request: CompanyCreate):
        existing = self.repository.get_by_ticker(request.ticker)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticker already exists.",
            )
        company = Company(name=request.name, ticker=request.ticker, sector=request.sector)
        return await self.repository.create(company)
