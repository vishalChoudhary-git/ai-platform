import pytest

from app.plugins.expenses.schemas import ExpenseApprovalDecision


def test_approval_accepts_manager_approval_without_reason() -> None:
    decision = ExpenseApprovalDecision(decision="approved")
    decision.validate_for_decision()


def test_approval_requires_reason_for_rejection() -> None:
    decision = ExpenseApprovalDecision(decision="rejected")

    with pytest.raises(ValueError, match="reason is required"):
        decision.validate_for_decision()
