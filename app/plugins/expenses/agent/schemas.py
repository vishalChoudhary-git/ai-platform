from typing import Any

from pydantic import BaseModel, Field

from app.plugins.expenses.models import ExpenseRequiredAction, ExpenseStatus


class AgentDecision(BaseModel):
    status: ExpenseStatus
    reason: str = Field(min_length=1)
    required_action: ExpenseRequiredAction = ExpenseRequiredAction.NONE
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
