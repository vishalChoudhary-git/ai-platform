from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.features.expenses.models.enums import ExpenseStatus


class ExpenseDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    expense_id: str
    employee_name: str
    employee_email: str
    manager_email: str
    category: str
    description: str
    amount: Decimal | None
    currency: str | None
    expense_date: date | None
    status: ExpenseStatus
    created_at: datetime
    updated_at: datetime
    documents: list[ExpenseDocumentResponse]
