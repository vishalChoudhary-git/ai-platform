import logging

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.agent import ExpenseAgent
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
    ) -> None:
        self.session = session
        self.expense_service = expense_service
        self.knowledge_service = knowledge_service
        self.redis = redis

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
        await self.session.commit()

        logger.info(
            "ExpenseResolutionService.resolve: persisted expense_id=%s status=%s required_action=%s",
            expense_id,
            expense.status.value,
            expense.required_action.value,
        )
