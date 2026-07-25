from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.domain.models.company import Company


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page, size, sector: str | None = None) -> list[Company]:
        query = select(Company)
        if sector:
            query = query.where(Company.sector == sector)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        print(f"result============== {result}")
        return list(result.scalars().all())

    async def get_by_ticker(self, ticker: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.ticker == ticker))
        return result.scalar_one_or_none()

    async def create(self, company: Company) -> Company:
        self.db.add(company)
        await self.db.commit()
        await self.db.refresh(company)

        return company
