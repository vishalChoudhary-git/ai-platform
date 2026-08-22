from datetime import date
from decimal import Decimal

from app.plugins.expenses.schemas import ExpenseCreateData, ExpenseUpdateData


def test_expense_create_data_normalizes_currency() -> None:
    request = ExpenseCreateData(
        employee_name="Vishal Choudhary",
        employee_email="vishal@example.com",
        manager_email="manager@example.com",
        category="hotel",
        description="Business travel hotel expense",
        amount="12500.00",
        currency="inr",
        expense_date=date(2026, 8, 15),
    )

    assert request.amount == Decimal("12500.00")
    assert request.currency == "INR"


def test_expense_create_data_defaults_currency_to_inr() -> None:
    request = ExpenseCreateData(
        employee_name="Vishal Choudhary",
        employee_email="vishal@example.com",
        manager_email="manager@example.com",
        category="hotel",
        description="Business travel hotel expense",
        amount="12500.00",
    )

    assert request.currency == "INR"


def test_expense_update_data_allows_document_only_follow_up() -> None:
    update = ExpenseUpdateData()

    assert update.model_fields_set == set()
