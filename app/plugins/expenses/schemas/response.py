from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.plugins.expenses.models.enums import (
    ExpenseApprovalStatus,
    ExpenseDocumentRole,
    ExpenseRequiredAction,
    ExpenseStatus,
)


class ExpenseDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    role: ExpenseDocumentRole


class ExpenseApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    approver_email: str
    status: ExpenseApprovalStatus
    reason: str | None
    requested_at: datetime
    resolved_at: datetime | None


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
    decision_reason: str | None
    required_action: ExpenseRequiredAction
    decision_evidence: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    documents: list[ExpenseDocumentResponse]
    approvals: list[ExpenseApprovalResponse]
