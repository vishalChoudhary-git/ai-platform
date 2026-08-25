from typing import Literal

from pydantic import BaseModel, Field


class ExpenseApprovalDecision(BaseModel):
    decision: Literal["approved", "rejected"]
    reason: str | None = Field(default=None, max_length=2000)

    def validate_for_decision(self) -> None:
        if self.decision == "rejected" and not self.reason:
            raise ValueError("A reason is required when rejecting an expense.")
