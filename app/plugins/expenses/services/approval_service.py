from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.notifications import SmtpEmailSender

from ..models import ExpenseApproval, ExpenseApprovalStatus, ExpenseRequiredAction, ExpenseStatus
from ..notifications import ExpenseNotificationService
from ..schemas import ExpenseApprovalDecision
from .expense_service import ExpenseService


class ExpenseApprovalService:
    def __init__(self, session: AsyncSession, expense_service: ExpenseService) -> None:
        self.session = session
        self.expense_service = expense_service
        self.notification_service = ExpenseNotificationService(SmtpEmailSender.from_settings())

    async def decide(
        self,
        expense_id: str,
        approver_email: str,
        decision: ExpenseApprovalDecision,
    ):
        decision.validate_for_decision()

        approver_email = approver_email.strip().lower()
        expense = await self.expense_service.get_by_business_id(expense_id)
        if expense.required_action != ExpenseRequiredAction.MANAGER_DECISION:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This expense does not currently require manager decision.",
            )

        approval = await self.session.scalar(
            select(ExpenseApproval)
            .where(
                ExpenseApproval.expense_id == expense.id,
                func.lower(ExpenseApproval.approver_email) == approver_email,
                ExpenseApproval.status == ExpenseApprovalStatus.PENDING,
            )
            .limit(1)
        )
        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No pending manager approval exists for this user and expense.",
            )

        approval.status = (
            ExpenseApprovalStatus.APPROVED
            if decision.decision == "approved"
            else ExpenseApprovalStatus.REJECTED
        )
        approval.reason = decision.reason
        approval.resolved_at = datetime.now(timezone.utc)

        expense.status = (
            ExpenseStatus.APPROVED
            if decision.decision == "approved"
            else ExpenseStatus.REJECTED
        )
        expense.required_action = ExpenseRequiredAction.NONE
        if decision.reason:
            expense.decision_reason = f"Manager decision: {decision.reason}"

        await self.session.commit()
        await self.notification_service.send_decision_notification(expense)
        return expense
