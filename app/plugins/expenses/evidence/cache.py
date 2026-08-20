import json
from typing import Any
from uuid import UUID

from redis.asyncio import Redis
from pydantic import BaseModel, Field


class ExpenseEvidence(BaseModel):
    expense_id: str
    document_id: UUID
    document_type: str | None = None
    merchant: str | None = None
    amount: str | None = None
    currency: str | None = None
    expense_date: str | None = None
    fields: dict[str, Any] = Field(default_factory=dict)


class ExpenseEvidenceCache:
    PREFIX = "expense:evidence:"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    @classmethod
    def key(cls, expense_id: str, document_id: UUID) -> str:
        return f"{cls.PREFIX}{expense_id}:{document_id}"

    async def get(self, expense_id: str, document_id: UUID) -> ExpenseEvidence | None:
        value = await self.redis.get(self.key(expense_id, document_id))
        if value is None:
            return None
        return ExpenseEvidence.model_validate_json(value)

    async def set(self, evidence: ExpenseEvidence) -> None:
        await self.redis.set(
            self.key(evidence.expense_id, evidence.document_id),
            evidence.model_dump_json(),
        )
