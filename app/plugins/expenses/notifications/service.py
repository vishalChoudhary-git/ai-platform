import asyncio
import logging
from typing import Any

from app.core.config import get_settings
from app.core.notifications import EmailMessageData, EmailSender
from app.plugins.expenses.models import Expense, ExpenseRequiredAction, ExpenseStatus

logger = logging.getLogger(__name__)


class ExpenseNotificationService:
    def __init__(self, email_sender: EmailSender) -> None:
        self.email_sender = email_sender

    async def send_decision_notification(self, expense: Expense) -> None:
        messages = [self._employee_message(expense)]
        if self._manager_should_be_notified(expense):
            messages.append(self._manager_message(expense))

        settings = get_settings()
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
                "ExpenseNotificationService.send_decision_notification: complete expense_id=%s recipients=%s",
                expense.expense_id,
                len(messages),
            )

    @staticmethod
    def _manager_should_be_notified(expense: Expense) -> bool:
        return (
            expense.status in {ExpenseStatus.APPROVED, ExpenseStatus.REJECTED}
            or expense.required_action == ExpenseRequiredAction.MANAGER_DECISION
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
    def _extract_policy_references(expense: Expense) -> list[dict[str, Any]]:
        references: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str, str]] = set()
        for item in expense.decision_evidence or []:
            if not isinstance(item, dict) or not item.get("policy_id"):
                continue
            key = (
                str(item.get("policy_id") or ""),
                str(item.get("version") or ""),
                str(item.get("rule_applied") or ""),
                str(item.get("condition") or ""),
                str(item.get("action") or ""),
            )
            if key not in seen:
                seen.add(key)
                references.append(item)
        return references

    @classmethod
    def _policy_reference_section(cls, expense: Expense) -> str:
        references = cls._extract_policy_references(expense)
        if not references:
            return "Policy reference: Not available in the decision evidence."

        sections: list[str] = []
        for index, reference in enumerate(references, start=1):
            sections.append(
                "\n".join(
                    [
                        f"Policy reference {index}:",
                        f"Policy ID: {reference.get('policy_id') or 'Not provided'}",
                        f"Version: {reference.get('version') or 'Not provided'}",
                        f"Rule applied: {reference.get('rule_applied') or 'Not provided'}",
                        f"Condition: {reference.get('condition') or 'Not provided'}",
                        f"Policy action: {reference.get('action') or 'Not provided'}",
                    ]
                )
            )
        return "\n\n".join(sections)

    @staticmethod
    def _display_amount(expense: Expense) -> str:
        currency = expense.currency or "INR"
        if expense.amount is not None:
            return f"{currency} {expense.amount}"

        for item in expense.decision_evidence or []:
            if not isinstance(item, dict):
                continue
            amount = item.get("amount")
            if amount is None:
                continue
            evidence_currency = item.get("currency") or currency
            return f"{evidence_currency} {amount} (from receipt evidence)"

        return "Not provided"

    @classmethod
    def _manager_message(cls, expense: Expense) -> EmailMessageData:
        required_action = expense.required_action

        if required_action == ExpenseRequiredAction.MANAGER_DECISION:
            subject = f"Action Required: Expense {expense.expense_id} - Policy Review"
            action_section = (
                "ACTION REQUIRED: POLICY REVIEW\n\n"
                "The automated expense review identified a policy exception "
                "and requires your decision.\n\n"
                f"Policy finding:\n{expense.decision_reason or 'No additional reason provided.'}\n\n"
                "Required action: Manager approval or rejection is required."
            )
        elif expense.status == ExpenseStatus.REJECTED:
            subject = f"Expense {expense.expense_id} - Rejected"
            action_section = (
                "FINAL MANAGER DECISION\n\n"
                "This expense was rejected by the manager.\n\n"
                f"Decision reason:\n{expense.decision_reason or 'No additional reason provided.'}"
            )
        elif required_action in {
            ExpenseRequiredAction.ADDITIONAL_INFORMATION,
            ExpenseRequiredAction.ADDITIONAL_DOCUMENT,
        }:
            subject = f"Expense {expense.expense_id} - Review Notice"
            action_section = (
                "REVIEW NOTICE\n\n"
                "The automated expense review identified a policy exception or incomplete evidence.\n\n"
                f"Finding:\n{expense.decision_reason or 'No additional reason provided.'}\n\n"
                f"Required action: {required_action.value}.\n"
                "Additional employee information/evidence is required before the expense can be finalized."
            )
        else:
            subject = f"Expense {expense.expense_id} - {expense.status.value}"
            action_section = "No manager action is currently required."

        policy_section = cls._policy_reference_section(expense)

        return EmailMessageData(
            to=expense.manager_email,
            subject=subject,
            body=(
                "Hello,\n\n"
                f"Expense {expense.expense_id} for {expense.employee_name} has been evaluated.\n\n"
                "Expense details:\n"
                f"Employee: {expense.employee_name}\n"
                f"Amount: {cls._display_amount(expense)}\n"
                f"Category: {expense.category}\n"
                f"Status: {expense.status.value}\n"
                f"Required action: {required_action.value}\n\n"
                f"{action_section}\n\n"
                f"Policy reference used for this evaluation:\n\n{policy_section}\n\n"
                "Please review the expense through the Expense workflow/API.\n"
            ),
        )
