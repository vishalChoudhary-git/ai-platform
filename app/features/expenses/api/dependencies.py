from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.expenses.services import ExpenseService


def get_expense_service(
    session: AsyncSession = Depends(get_db),
) -> ExpenseService:
    return ExpenseService(session)
