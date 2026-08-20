from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.documents.api.dependencies import get_document_service
from app.features.documents.services import DocumentService

from .service import ExpensePolicyService


def get_policy_service(
    session: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> ExpensePolicyService:
    return ExpensePolicyService(session, document_service)
