from dataclasses import dataclass, field
from typing import Any

from app.plugins.expenses.models import Expense


@dataclass
class ExpenseAgentState:
    expense: Expense
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
