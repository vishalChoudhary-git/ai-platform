import pytest

from app.core.notifications import EmailMessageData
from app.plugins.expenses.models import ExpenseRequiredAction, ExpenseStatus
from app.plugins.expenses.notifications import ExpenseNotificationService


class FakeEmailSender:
    def __init__(self, failures: dict[str, Exception] | None = None) -> None:
        self.messages: list[EmailMessageData] = []
        self.failures = failures or {}

    async def send(self, message: EmailMessageData) -> None:
        failure = self.failures.get(message.to)
        if failure:
            raise failure
        self.messages.append(message)


class FakeExpense:
    expense_id = "EXP-TEST123"
    employee_name = "Test Employee"
    employee_email = "employee@example.com"
    manager_email = "manager@example.com"
    amount = None
    currency = None
    category = "Hotel"
    status = ExpenseStatus.INFORMATION_REQUIRED
    decision_reason = "Hotel expense exceeds the applicable policy limit."
    required_action = ExpenseRequiredAction.MANAGER_DECISION
    decision_evidence = [
        {
            "amount": "25000",
            "currency": "INR",
            "merchant": "Test Hotel",
            "policy_id": "POL-TEST",
            "version": "2026.1",
            "rule_applied": "R1",
            "condition": "Hotel expense above INR 15,000 requires manager approval.",
            "action": "Manager approval required",
        }
    ]


class ClarificationExpense(FakeExpense):
    required_action = ExpenseRequiredAction.ADDITIONAL_INFORMATION
    decision_reason = "Expense details need confirmation."


@pytest.mark.asyncio
async def test_manager_decision_notifies_employee_and_manager() -> None:
    sender = FakeEmailSender()
    service = ExpenseNotificationService(sender)

    await service.send_decision_notification(FakeExpense())

    assert [message.to for message in sender.messages] == [
        "employee@example.com",
        "manager@example.com",
    ]
    assert all("EXP-TEST123" in message.subject for message in sender.messages)

    manager_message = sender.messages[1]
    assert "Policy ID: POL-TEST" in manager_message.body
    assert "Version: 2026.1" in manager_message.body
    assert "Rule applied: R1" in manager_message.body
    assert "INR 25000 (from receipt evidence)" in manager_message.body


@pytest.mark.asyncio
async def test_additional_information_does_not_notify_manager() -> None:
    sender = FakeEmailSender()
    service = ExpenseNotificationService(sender)

    await service.send_decision_notification(ClarificationExpense())

    assert [message.to for message in sender.messages] == ["employee@example.com"]


@pytest.mark.asyncio
async def test_missing_expense_currency_defaults_to_inr_for_display() -> None:
    expense = FakeExpense()
    expense.amount = 4550
    expense.currency = None
    expense.decision_evidence = [
        {
            "policy_id": "POL-TEST",
            "version": "2026.1",
            "rule_applied": "R1",
            "condition": "Hotel limit exceeded.",
            "action": "Manager approval required",
        }
    ]

    message = ExpenseNotificationService._manager_message(expense)

    assert "Amount: INR 4550" in message.body


@pytest.mark.asyncio
async def test_policy_references_with_same_identity_are_deduplicated() -> None:
    expense = FakeExpense()
    expense.decision_evidence = [
        {
            "policy_id": "POL-TEST",
            "version": "2026.1",
            "rule_applied": "R1",
            "condition": "Hotel limit exceeded.",
            "action": "Manager approval required",
            "source": "agent",
        },
        {
            "policy_id": "POL-TEST",
            "version": "2026.1",
            "rule_applied": "R1",
            "condition": "Hotel limit exceeded.",
            "action": "Manager approval required",
            "source": "resolution",
        },
    ]

    message = ExpenseNotificationService._manager_message(expense)

    assert message.body.count("Policy reference 1:") == 1
    assert "Policy reference 2:" not in message.body


@pytest.mark.asyncio
async def test_one_recipient_failure_does_not_block_other_recipient() -> None:
    sender = FakeEmailSender(
        failures={"employee@example.com": RuntimeError("employee delivery failed")}
    )
    service = ExpenseNotificationService(sender)

    await service.send_decision_notification(FakeExpense())

    assert [message.to for message in sender.messages] == ["manager@example.com"]
