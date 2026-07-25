from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.modules.knowledge.repositories.company_repository import CompanyRepository
from app.modules.knowledge.services.company_service import CompanyService


def get_company_repository(db: AsyncSession = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(db)


def get_company_service(
    repository: CompanyRepository = Depends(get_company_repository),
) -> CompanyService:
    return CompanyService(repository)
