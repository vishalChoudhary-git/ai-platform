import asyncio
import logging
from typing import Any

from app.core.notifications import EmailMessageData, EmailSender
from app.plugins.expenses.models import Expense

logger = logging.getLogger(__name__)


class ExpenseNotificationService:
    def __init__(self, email_sender: EmailSender) -> None:
        self.email_sender = email_sender

    async def send_decision_notification(self, expense: Expense) -> None:
        messages = [self._employee_message(expense), self._manager_message(expense)]
        results = await asyncio.gather(
            *(self.email_sender.send(message) for message in messages),
            return_exceptions=True,
        )

        failures = [result for result in results if isinstance(result, Exception)]
        if failures:
            logger.error(
                "ExpenseNotificationService.send_decision_notification: failures expense_id=%s count=%s",
                expense.expense_id,
                len(failures),
            )
            for failure in failures:
                logger.error(
                    "ExpenseNotificationService.send_decision_notification: delivery failure expense_id=%s error=%s",
                    expense.expense_id,
                    failure,
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
        requires_manager_decision = expense.required_action.value == "manager_decision"
        policy_details = ExpenseNotificationService._policy_details(expense)

        if requires_manager_decision:
            subject = f"Action Required: Expense {expense.expense_id} - Policy Review"
            action_section = (
                "ACTION REQUIRED: POLICY REVIEW\n\n"
                "The automated expense review identified a policy exception "
                "and requires your decision.\n\n"
                f"Policy reference:\n{policy_details}\n\n"
                f"Policy finding:\n{expense.decision_reason or 'No additional reason provided.'}\n\n"
                "Required action: Manager approval or rejection is required."
            )
        else:
            subject = f"Expense {expense.expense_id} - {expense.status.value}"
            action_section = "No manager action is currently required."

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
                f"Required action: {expense.required_action.value}\n\n"
                f"{action_section}\n\n"
                "Please review the expense through the Expense workflow/API.\n"
            ),
        )

    @staticmethod
    def _policy_details(expense: Expense) -> str:
        evidence = expense.decision_evidence or []
        if isinstance(evidence, dict):
            evidence = [evidence]

        policy_items: list[str] = []
        for item in evidence:
            if not isinstance(item, dict) or "policy_id" not in item:
                continue

            policy_id = item.get("policy_id", "unknown")
            version = item.get("version", "unknown")
            effective_from = item.get("effective_from")
            rule_applied = item.get("rule_applied", "unknown")
            condition = item.get("condition", "unknown")
            action = item.get("action") or item.get("rule_action") or "unknown"

            policy_items.append(
                "Policy ID: {policy_id}\n"
                "Version: {version}\n"
                "Effective from: {effective_from}\n"
                "Rule applied: {rule_applied}\n"
                "Condition: {condition}\n"
                "Policy action: {action}".format(
                    policy_id=policy_id,
                    version=version,
                    effective_from=effective_from or "not specified",
                    rule_applied=rule_applied,
                    condition=condition,
                    action=action,
                )
            )

        if policy_items:
            return "\n\n".join(policy_items)

        return "Policy reference was not included in the final agent evidence."
