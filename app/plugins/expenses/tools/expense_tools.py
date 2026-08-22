import logging
from datetime import date
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.evidence.cache import ExpenseEvidenceCache
from app.plugins.expenses.policy.cache import ExpensePolicyCache
from app.plugins.expenses.policy.enums import ExpensePolicyStatus
from app.plugins.expenses.policy.models import ExpensePolicy
from app.plugins.expenses.services import ExpenseService

logger = logging.getLogger(__name__)

DEFAULT_EXPENSE_CURRENCY = "INR"


class ExpenseAgentTools:
    def __init__(
        self,
        expense_service: ExpenseService,
        knowledge_service: KnowledgeService,
        session: AsyncSession,
        redis: Redis,
    ) -> None:
        self.expense_service = expense_service
        self.knowledge_service = knowledge_service
        self.session = session
        self.evidence_cache = ExpenseEvidenceCache(redis)
        self.policy_cache = ExpensePolicyCache(redis)

    async def get_expense(self, expense_id: str) -> dict[str, Any]:
        logger.info("ExpenseAgentTools.get_expense: start expense_id=%s", expense_id)
        expense = await self.expense_service.get_by_business_id(expense_id)
        result = {
            "expense_id": expense.expense_id,
            "employee_name": expense.employee_name,
            "employee_email": expense.employee_email,
            "manager_email": expense.manager_email,
            "category": expense.category,
            "description": expense.description,
            "amount": str(expense.amount) if expense.amount is not None else None,
            "currency": expense.currency or DEFAULT_EXPENSE_CURRENCY,
            "expense_date": expense.expense_date.isoformat() if expense.expense_date else None,
            "status": expense.status.value,
            "documents": [
                {"document_id": str(document.document_id), "role": document.role.value}
                for document in expense.documents
            ],
            "approvals": [
                {
                    "approver_email": approval.approver_email,
                    "status": approval.status.value,
                    "reason": approval.reason,
                }
                for approval in expense.approvals
            ],
        }
        logger.info(
            "ExpenseAgentTools.get_expense: complete expense_id=%s documents=%s approvals=%s",
            expense_id,
            len(result["documents"]),
            len(result["approvals"]),
        )
        return result

    async def get_expense_evidence(self, expense_id: str) -> dict[str, Any]:
        logger.info("ExpenseAgentTools.get_expense_evidence: start expense_id=%s", expense_id)
        expense = await self.expense_service.get_by_business_id(expense_id)
        evidence = []
        missing_documents = []

        for document in expense.documents:
            item = await self.evidence_cache.get(expense_id, document.document_id)
            if item is None:
                missing_documents.append(str(document.document_id))
                continue
            evidence.append(item.model_dump(mode="json"))

        result = {
            "expense_id": expense_id,
            "evidence": evidence,
            "missing_documents": missing_documents,
        }
        logger.info(
            "ExpenseAgentTools.get_expense_evidence: complete expense_id=%s evidence=%s missing=%s",
            expense_id,
            len(evidence),
            len(missing_documents),
        )
        return result

    async def get_expense_policy(self, expense_id: str) -> dict[str, Any]:
        logger.info("ExpenseAgentTools.get_expense_policy: start expense_id=%s", expense_id)
        expense = await self.expense_service.get_by_business_id(expense_id)
        effective_date = expense.expense_date or date.today()

        policy = await self.session.scalar(
            select(ExpensePolicy)
            .where(
                ExpensePolicy.status == ExpensePolicyStatus.PUBLISHED,
                or_(
                    ExpensePolicy.effective_from.is_(None),
                    ExpensePolicy.effective_from <= effective_date,
                ),
                or_(
                    ExpensePolicy.effective_to.is_(None),
                    ExpensePolicy.effective_to >= effective_date,
                ),
            )
            .order_by(ExpensePolicy.effective_from.desc().nullslast())
            .limit(1)
        )
        if policy is None:
            return {"expense_id": expense_id, "policy": None}

        snapshot = await self.policy_cache.get(policy.checksum)
        if snapshot is None:
            return {
                "expense_id": expense_id,
                "policy": None,
                "error": "Published policy is not available in the cache.",
            }

        result = {
            "expense_id": expense_id,
            "policy": {
                "policy_id": snapshot.policy_id,
                "version": snapshot.version,
                "checksum": snapshot.checksum,
                "effective_from": snapshot.effective_from,
                "rules": [rule.model_dump() for rule in snapshot.rules],
            },
        }
        logger.info(
            "ExpenseAgentTools.get_expense_policy: complete expense_id=%s policy=%s rules=%s",
            expense_id,
            snapshot.policy_id,
            len(snapshot.rules),
        )
        return result

    async def search_expense_policy(self, query: str) -> dict[str, Any]:
        logger.info("ExpenseAgentTools.search_expense_policy: start")
        response = await self.knowledge_service.query(query=query)
        result = {
            "answer": response.answer,
            "sources": [
                {
                    "source_index": source.source_index,
                    "chunk_id": str(source.chunk_id),
                    "document_id": str(source.document_id),
                    "page_number": source.page_number,
                    "chunk_index": source.chunk_index,
                    "text": source.text,
                }
                for source in response.sources
            ],
        }
        logger.info(
            "ExpenseAgentTools.search_expense_policy: complete sources=%s",
            len(result["sources"]),
        )
        return result
