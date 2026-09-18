from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from app.plugins.expenses.models.enums import (
    ExpenseDocumentRole,
    ExpenseRequiredAction,
    ExpenseStatus,
)
from app.plugins.expenses.schemas import ExpenseResponse


def test_expense_response_accepts_list_decision_evidence() -> None:
    expense_id = uuid4()
    document_id = uuid4()
    now = datetime.now(UTC)

    response = ExpenseResponse.model_validate(
        {
            "id": expense_id,
            "expense_id": "EXP-TEST123",
            "employee_name": "Test User",
            "employee_email": "test@example.com",
            "manager_email": "manager@example.com",
            "category": "meals",
            "description": "Lunch",
            "amount": Decimal("1350.00"),
            "currency": "INR",
            "expense_date": date(2026, 8, 18),
            "status": ExpenseStatus.APPROVED,
            "decision_reason": "Within policy limit.",
            "required_action": ExpenseRequiredAction.NONE,
            "decision_evidence": [
                {"type": "receipt", "amount": "1350"},
                {"type": "policy_rule", "rule_applied": "R1"},
            ],
            "created_at": now,
            "updated_at": now,
            "documents": [
                {
                    "id": uuid4(),
                    "document_id": document_id,
                    "role": ExpenseDocumentRole.RECEIPT,
                }
            ],
            "approvals": [],
        }
    )

    assert response.status == ExpenseStatus.APPROVED
    assert response.decision_evidence is not None
    assert len(response.decision_evidence) == 2
    assert response.decision_evidence[0]["type"] == "receipt"
