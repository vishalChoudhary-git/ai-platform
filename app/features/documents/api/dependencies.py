from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.documents.repositories import DocumentRepository
from app.features.documents.repositories.company_repository import CompanyRepository
from app.features.documents.services import DocumentService
from app.features.documents.services.company_service import CompanyService


def get_company_repository(db: AsyncSession = Depends(get_db)) -> CompanyRepository:
    return CompanyRepository(db)


def get_company_service(
    repository: CompanyRepository = Depends(get_company_repository),
) -> CompanyService:
    return CompanyService(repository)


def get_document_repository(
    session: AsyncSession = Depends(get_db),
) -> DocumentRepository:
    return DocumentRepository(session)


def get_document_service(
    repository: DocumentRepository = Depends(
        get_document_repository,
    ),
) -> DocumentService:
    return DocumentService(repository)
