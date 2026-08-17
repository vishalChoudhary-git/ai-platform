from uuid import uuid4

from app.features.expenses.schemas import ExpenseCreateRequest


def test_expense_request_requires_at_least_one_document() -> None:
    request_data = {
        "employee_name": "Vishal Choudhary",
        "employee_email": "vishal@example.com",
        "manager_email": "manager@example.com",
        "category": "hotel",
        "description": "Business travel hotel expense",
        "document_ids": [],
    }

    try:
        ExpenseCreateRequest.model_validate(request_data)
    except ValueError:
        return

    raise AssertionError("ExpenseCreateRequest should require at least one document")


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
