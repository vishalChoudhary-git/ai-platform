from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.agent.agent import ExpenseAgent
from app.plugins.expenses.models import ExpenseRequiredAction, ExpenseStatus
from app.plugins.expenses.services import ExpenseService
from app.plugins.expenses.tools import ExpenseAgentTools


@pytest.mark.asyncio
async def test_get_expense_tool_returns_structured_expense_context() -> None:
    document_id = uuid4()
    expense = SimpleNamespace(
        expense_id="EXP-001",
        employee_name="Vishal Choudhary",
        employee_email="vishal@example.com",
        manager_email="manager@example.com",
        category="hotel",
        description="Business trip",
        amount=12000,
        currency="INR",
        expense_date=None,
        status=ExpenseStatus.SUBMITTED,
        documents=[
            SimpleNamespace(document_id=document_id, role=SimpleNamespace(value="receipt")),
        ],
        approvals=[],
    )

    class FakeExpenseService:
        async def get_by_business_id(self, expense_id: str):
            assert expense_id == "EXP-001"
            return expense

    class FakeKnowledgeService:
        async def query(self, query: str):
            raise AssertionError("Knowledge search should not be called")

    tools = ExpenseAgentTools(
        cast(ExpenseService, FakeExpenseService()),
        cast(KnowledgeService, FakeKnowledgeService()),
        cast(AsyncSession, None),
        cast(Redis, None),
    )

    result = await tools.get_expense("EXP-001")

    assert result["expense_id"] == "EXP-001"
    assert result["category"] == "hotel"
    assert result["documents"][0]["document_id"] == str(document_id)


@pytest.mark.asyncio
async def test_search_expense_policy_maps_grounded_sources() -> None:
    document_id = uuid4()
    chunk_id = uuid4()
    source = SimpleNamespace(
        source_index=1,
        chunk_id=chunk_id,
        document_id=document_id,
        page_number=5,
        chunk_index=2,
        text="Hotel reimbursement limit is INR 15,000 per night.",
    )

    response = SimpleNamespace(
        answer="Hotel reimbursement is limited to INR 15,000 per night.",
        sources=[source],
    )

    class FakeExpenseService:
        pass

    class FakeKnowledgeService:
        async def query(self, query: str):
            assert query == "hotel reimbursement limit"
            return response

    tools = ExpenseAgentTools(
        cast(ExpenseService, FakeExpenseService()),
        cast(KnowledgeService, FakeKnowledgeService()),
        cast(AsyncSession, None),
        cast(Redis, None),
    )

    result = await tools.search_expense_policy("hotel reimbursement limit")

    assert result["sources"][0]["document_id"] == str(document_id)
    assert result["sources"][0]["page_number"] == 5
    assert "15,000" in result["answer"]


def test_agent_parses_structured_decision() -> None:
    decision = ExpenseAgent._parse_decision(
        '{"status":"information_required",'
        '"reason":"Hotel expense exceeds the standard limit.",'
        '"required_action":"manager_decision",'
        '"evidence":[{"claimed_amount":25000,"policy_limit":15000}],'
        '"missing_information":[]}'
    )

    assert decision.status == ExpenseStatus.INFORMATION_REQUIRED
    assert decision.required_action == ExpenseRequiredAction.MANAGER_DECISION
    assert decision.evidence[0]["policy_limit"] == 15000


def test_agent_normalizes_single_evidence_object() -> None:
    decision = ExpenseAgent._parse_decision(
        '{"status":"approved",'
        '"reason":"The expense complies with policy.",'
        '"evidence":{"claimed_amount":12000,"policy_limit":15000}}'
    )

    assert decision.evidence == [{"claimed_amount": 12000, "policy_limit": 15000}]
