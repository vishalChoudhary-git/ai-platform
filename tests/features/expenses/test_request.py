from uuid import uuid4

import pytest

from app.features.expenses.schemas import ExpenseCreateRequest


def test_expense_request_requires_at_least_one_document() -> None:
    with pytest.raises(ValueError):
        ExpenseCreateRequest.model_validate(
            {
                "employee_name": "Vishal Choudhary",
                "employee_email": "vishal@example.com",
                "manager_email": "manager@example.com",
                "category": "hotel",
                "description": "Business travel hotel expense",
                "document_ids": [],
            }
        )


def test_expense_request_normalizes_currency() -> None:
    request = ExpenseCreateRequest(
        employee_name="Vishal Choudhary",
        employee_email="vishal@example.com",
        manager_email="manager@example.com",
        category="hotel",
        description="Business travel hotel expense",
        document_ids=[uuid4()],
        amount="12500.00",
        currency="inr",
    )

    assert request.currency == "INR"
