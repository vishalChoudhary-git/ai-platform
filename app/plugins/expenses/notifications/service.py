import asyncio
import logging

from app.core.notifications import EmailMessageData, EmailSender
from app.plugins.expenses.models import Expense

logger = logging.getLogger(__name__)


class ExpenseNotificationService:
    def __init__(self, email_sender: EmailSender) -> None:
        self.email_sender = email_sender

    async def send_decision_notification(self, expense: Expense) -> None:
        employee = self._employee_message(expense)
        manager = self._manager_message(expense)

        results = await asyncio.gather(
            self.email_sender.send(employee),
            self.email_sender.send(manager),
            return_exceptions=True,
        )

        failures = [result for result in results if isinstance(result, Exception)]
        if failures:
            logger.error(
                "ExpenseNotificationService.send_decision_notification: failed expense_id=%s failures=%s",
                expense.expense_id,
                len(failures),
            )
            for failure in failures:
                logger.exception(
                    "ExpenseNotificationService.send_decision_notification: email delivery failure",
                    exc_info=failure,
                )
        else:
            logger.info(
                "ExpenseNotificationService.send_decision_notification: complete expense_id=%s recipients=2",
                expense.expense_id,
            )

    @staticmethod
    def _employee_message(expense: Expense) -> EmailMessageData:
        return EmailMessageData(
            to=expense.employee_email,
            subject=f"Expense {expense.expense_id} - {expense.status.value}",
            body=(
                f"Hello {expense.employee_name},\n\n"
                f"Your expense {expense.expense_id} has been evaluated.\n\n"
                f"Status: {expense.status.value}\n"
                f"Reason: {expense.decision_reason or 'No additional reason provided.'}\n"
                f"Required action: {expense.required_action.value}\n\n"
                "You can check the latest expense status through the Expense API.\n"
            ),
        )

    @staticmethod
    def _manager_message(expense: Expense) -> EmailMessageData:
        action_message = (
            "Manager decision is required for this expense."
            if expense.required_action.value == "manager_decision"
            else "No manager action is currently required."
        )
        return EmailMessageData(
            to=expense.manager_email,
            subject=f"Expense {expense.expense_id} - {expense.status.value}",
            body=(
                f"Hello,\n\n"
                f"Expense {expense.expense_id} for {expense.employee_name} has been evaluated.\n\n"
                f"Status: {expense.status.value}\n"
                f"Amount: {expense.amount} {expense.currency or ''}\n"
                f"Category: {expense.category}\n"
                f"Reason: {expense.decision_reason or 'No additional reason provided.'}\n"
                f"Required action: {expense.required_action.value}\n\n"
                f"{action_message}\n"
            ),
        )
