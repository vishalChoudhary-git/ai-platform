from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.documents.api.dependencies import get_document_service
from app.features.documents.services import DocumentService
from app.plugins.expenses.services import ExpenseApprovalService, ExpenseService


def get_expense_service(
    session: AsyncSession = Depends(get_db),
    document_service: DocumentService = Depends(get_document_service),
) -> ExpenseService:
    return ExpenseService(
        session=session,
        document_service=document_service,
    )


def get_expense_approval_service(
    session: AsyncSession = Depends(get_db),
    expense_service: ExpenseService = Depends(get_expense_service),
) -> ExpenseApprovalService:
    return ExpenseApprovalService(
        session=session,
        expense_service=expense_service,
    )
