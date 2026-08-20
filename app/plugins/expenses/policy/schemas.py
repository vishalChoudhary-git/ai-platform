from typing import Any

from pydantic import BaseModel, Field


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
