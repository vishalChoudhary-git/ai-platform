from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.documents.api.dependencies import get_document_service
from app.features.documents.services import DocumentService
from app.plugins.expenses.services import ExpenseService


def get_expense_service(
    session: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> ExpenseService:
    return ExpenseService(
        session=session,
        document_service=document_service,
    )
