import logging

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.agent.agent import ExpenseAgent
from app.plugins.expenses.models import ExpenseApproval, ExpenseApprovalStatus, ExpenseRequiredAction
from app.plugins.expenses.notifications import ExpenseNotificationService
from app.plugins.expenses.services import ExpenseService
from app.plugins.expenses.tools import ExpenseAgentTools

logger = logging.getLogger(__name__)


class ExpenseResolutionService:
    def __init__(
        self,
        session: AsyncSession,
        expense_service: ExpenseService,
        knowledge_service: KnowledgeService,
        redis: Redis,
        notification_service: ExpenseNotificationService,
    ) -> None:
        self.session = session
        self.expense_service = expense_service
        self.knowledge_service = knowledge_service
        self.redis = redis
        self.notification_service = notification_service

    async def resolve(self, expense_id: str) -> None:
        logger.info("ExpenseResolutionService.resolve: start expense_id=%s", expense_id)
        tools = ExpenseAgentTools(
            self.expense_service,
            self.knowledge_service,
            self.session,
            self.redis,
        )
        agent = ExpenseAgent(
            expense_service=self.expense_service,
            knowledge_service=self.knowledge_service,
            session=self.session,
            redis=self.redis,
            tools=tools,
        )
        decision = await agent.resolve(expense_id)

        expense = await self.expense_service.get_by_business_id(expense_id)
        expense.status = decision.status
        expense.decision_reason = decision.reason
        expense.required_action = decision.required_action
        expense.decision_evidence = decision.evidence

        if decision.required_action == ExpenseRequiredAction.MANAGER_DECISION:
            existing_pending = await self.session.scalar(
                select(ExpenseApproval.id).where(
                    ExpenseApproval.expense_id == expense.id,
                    ExpenseApproval.approver_email == expense.manager_email,
                    ExpenseApproval.status == ExpenseApprovalStatus.PENDING,
                )
            )
            if existing_pending is None:
                self.session.add(
                    ExpenseApproval(
                        expense_id=expense.id,
                        approver_email=expense.manager_email,
                        status=ExpenseApprovalStatus.PENDING,
                        reason=decision.reason,
                    )
                )
                logger.info(
                    "ExpenseResolutionService.resolve: manager_approval_created expense_id=%s manager=%s",
                    expense_id,
                    expense.manager_email,
                )
            else:
                logger.info(
                    "ExpenseResolutionService.resolve: manager_approval_exists expense_id=%s manager=%s",
                    expense_id,
                    expense.manager_email,
                )

        await self.session.commit()

        logger.info(
            "ExpenseResolutionService.resolve: persisted expense_id=%s status=%s required_action=%s",
            expense_id,
            expense.status.value,
            expense.required_action.value,
        )

        await self.notification_service.send_decision_notification(expense)
