import asyncio
import logging

from app.core.config import get_settings
from app.core.notifications import EmailMessageData, EmailSender
from app.plugins.expenses.models import Expense

logger = logging.getLogger(__name__)


class ExpenseNotificationService:
    def __init__(self, email_sender: EmailSender) -> None:
        self.email_sender = email_sender

    async def send_decision_notification(self, expense: Expense) -> None:
        settings = get_settings()
        messages = [self._employee_message(expense), self._manager_message(expense)]
        failures: list[Exception] = []

        for index, message in enumerate(messages):
            if index > 0 and settings.email_recipient_delay_seconds > 0:
                logger.info(
                    "ExpenseNotificationService.send_decision_notification: delaying next recipient expense_id=%s delay_seconds=%s",
                    expense.expense_id,
                    settings.email_recipient_delay_seconds,
                )
                await asyncio.sleep(settings.email_recipient_delay_seconds)

            try:
                await self.email_sender.send(message)
            except Exception as exc:
                failures.append(exc)
                logger.error(
                    "ExpenseNotificationService.send_decision_notification: delivery failure expense_id=%s recipient=%s error=%s",
                    expense.expense_id,
                    message.to,
                    exc,
                )

        if failures:
            logger.error(
                "ExpenseNotificationService.send_decision_notification: failures expense_id=%s count=%s",
                expense.expense_id,
                len(failures),
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
    def _policy_references(expense: Expense) -> list[str]:
        references: list[str] = []
        for item in expense.decision_evidence or []:
            if not isinstance(item, dict) or not item.get("policy_id"):
                continue
            reference = (
                "Policy ID: {policy_id}\n"
                "Version: {version}\n"
                "Rule applied: {rule}\n"
                "Condition: {condition}\n"
                "Policy action: {action}"
            ).format(
                policy_id=item["policy_id"],
                version=item.get("version") or "unknown",
                rule=item.get("rule_applied") or "unknown",
                condition=item.get("condition") or "unknown",
                action=item.get("action") or "unknown",
            )
            if reference not in references:
                references.append(reference)
        return references

    @classmethod
    def _manager_message(cls, expense: Expense) -> EmailMessageData:
        required_action = expense.required_action.value
        policy_references = cls._policy_references(expense)

        if required_action == "manager_decision":
            subject = f"Action Required: Expense {expense.expense_id} - Policy Review"
            action_section = (
                "ACTION REQUIRED: POLICY REVIEW\n\n"
                "The automated expense review identified a policy exception "
                "and requires your decision.\n\n"
                f"Policy finding:\n{expense.decision_reason or 'No additional reason provided.'}\n\n"
                "Required action: Manager approval or rejection is required."
            )
        elif required_action in {"additional_information", "additional_document"}:
            subject = f"Expense {expense.expense_id} - Review Notice"
            action_section = (
                "REVIEW NOTICE\n\n"
                "The automated expense review identified a policy exception or incomplete evidence.\n\n"
                f"Finding:\n{expense.decision_reason or 'No additional reason provided.'}\n\n"
                f"Required action: {required_action}.\n"
                "Additional employee information/evidence is required before the expense can be finalized."
            )
        else:
            subject = f"Expense {expense.expense_id} - {expense.status.value}"
            action_section = "No manager action is currently required."

        policy_section = ""
        if policy_references:
            policy_section = "\n\nPolicy reference used for this evaluation:\n\n" + "\n\n".join(policy_references)

        return EmailMessageData(
            to=expense.manager_email,
            subject=subject,
            body=(
                "Hello,\n\n"
                f"Expense {expense.expense_id} for {expense.employee_name} has been evaluated.\n\n"
                "Expense details:\n"
                f"Employee: {expense.employee_name}\n"
                f"Amount: {expense.amount} {expense.currency or ''}\n"
                f"Category: {expense.category}\n"
                f"Status: {expense.status.value}\n"
                f"Required action: {required_action}\n\n"
                f"{action_section}"
                f"{policy_section}\n\n"
                "Please review the expense through the Expense workflow/API.\n"
            ),
        )
