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
    amount = "25000"
    currency = "INR"
    category = "Hotel"
    status = ExpenseStatus.INFORMATION_REQUIRED
    decision_reason = "Hotel expense exceeds the applicable policy limit."
    required_action = ExpenseRequiredAction.MANAGER_DECISION


@pytest.mark.asyncio
async def test_decision_notification_targets_employee_and_manager() -> None:
    sender = FakeEmailSender()
    service = ExpenseNotificationService(sender)

    await service.send_decision_notification(FakeExpense())

    assert [message.to for message in sender.messages] == [
        "employee@example.com",
        "manager@example.com",
    ]
    assert all("EXP-TEST123" in message.subject for message in sender.messages)


@pytest.mark.asyncio
async def test_one_recipient_failure_does_not_block_other_recipient() -> None:
    sender = FakeEmailSender(
        failures={"employee@example.com": RuntimeError("employee delivery failed")}
    )
    service = ExpenseNotificationService(sender)

    await service.send_decision_notification(FakeExpense())

    assert [message.to for message in sender.messages] == ["manager@example.com"]
