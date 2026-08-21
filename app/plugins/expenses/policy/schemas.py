from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .enums import ExpensePolicyStatus


class PolicyRule(BaseModel):
    rule_id: str
    category: str
    condition: str
    action: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ExpensePolicySnapshot(BaseModel):
    policy_id: str
    version: str
    checksum: str
    effective_from: str | None = None
    rules: list[PolicyRule] = Field(default_factory=list)


class ExpensePolicyUploadData(BaseModel):
    policy_name: str = Field(min_length=1, max_length=255)
    version: str = Field(min_length=1, max_length=50)
    effective_from: date | None = None


class ExpensePolicyResponse(BaseModel):
    policy_id: str
    policy_name: str
    version: str
    document_id: UUID
    checksum: str
    effective_from: date | None
    status: ExpensePolicyStatus
    published_by: str
    published_at: datetime | None

    model_config = {"from_attributes": True}
