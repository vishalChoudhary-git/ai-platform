import json
import logging
from typing import Any

from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.services import ExpenseService
from app.plugins.expenses.tools import ExpenseAgentTools

from .schemas import AgentDecision
from .state import ExpenseAgentState

logger = logging.getLogger(__name__)


class ExpenseAgent:
    MAX_TOOL_ROUNDS = 6

    def __init__(
        self,
        expense_service: ExpenseService,
        knowledge_service: KnowledgeService,
        session: AsyncSession,
        redis: Redis,
        client: AsyncOpenAI | None = None,
        model: str | None = None,
        tools: ExpenseAgentTools | None = None,
    ) -> None:
        settings = get_settings()
        self.tools = tools or ExpenseAgentTools(
            expense_service,
            knowledge_service,
            session,
            redis,
        )
        self.client = client or AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.rag_llm_model
        logger.info(
            "ExpenseAgent.__init__: model=%s max_tool_rounds=%s",
            self.model,
            self.MAX_TOOL_ROUNDS,
        )

    async def resolve(self, expense_id: str) -> AgentDecision:
        logger.info("ExpenseAgent.resolve: start expense_id=%s", expense_id)

        expense = await self.tools.expense_service.get_by_business_id(expense_id)
        state = ExpenseAgentState(expense=expense)
        logger.info(
            "ExpenseAgent.resolve: expense_loaded expense_id=%s status=%s documents=%s approvals=%s",
            expense.expense_id,
            expense.status.value,
            len(expense.documents),
            len(expense.approvals),
        )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self._system_prompt()},
            {
                "role": "user",
                "content": f"Resolve expense {expense_id} according to company policy.",
            },
        ]
        logger.info("ExpenseAgent.resolve: initial_messages_prepared expense_id=%s", expense_id)

        for round_number in range(1, self.MAX_TOOL_ROUNDS + 1):
            logger.info(
                "ExpenseAgent.resolve: llm_call_start expense_id=%s round=%s",
                expense_id,
                round_number,
            )
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._tool_definitions(),
                tool_choice="auto",
                temperature=0,
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls or []
            logger.info(
                "ExpenseAgent.resolve: llm_call_complete expense_id=%s round=%s tool_calls=%s",
                expense_id,
                round_number,
                len(tool_calls),
            )

            messages.append(message.model_dump(exclude_none=True))

            if not tool_calls:
                decision = self._parse_decision(message.content)
                state.tool_results.append(
                    {"type": "final_decision", "status": decision.status.value}
                )
                logger.info(
                    "ExpenseAgent.resolve: final_decision expense_id=%s round=%s status=%s required_action=%s",
                    expense_id,
                    round_number,
                    decision.status.value,
                    decision.required_action.value,
                )
                return decision

            for tool_call in tool_calls:
                logger.info(
                    "ExpenseAgent._execute_tool: start expense_id=%s round=%s tool=%s call_id=%s",
                    expense_id,
                    round_number,
                    tool_call.function.name,
                    tool_call.id,
                )
                result = await self._execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    expense_id,
                )
                state.tool_results.append({"tool": tool_call.function.name, "result": result})
                logger.info(
                    "ExpenseAgent._execute_tool: complete expense_id=%s round=%s tool=%s",
                    expense_id,
                    round_number,
                    tool_call.function.name,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        logger.warning(
            "ExpenseAgent.resolve: max_tool_rounds_exceeded expense_id=%s max_rounds=%s",
            expense_id,
            self.MAX_TOOL_ROUNDS,
        )
        raise RuntimeError("Expense agent exceeded the maximum tool-call rounds.")

    @staticmethod
    def _system_prompt() -> str:
        return """You are the Expense Resolution Agent.

Your goal is to resolve an expense according to company policy.

You may investigate using the provided read-only tools. Decide what information you need and which tool to call. Do not invent policy rules or missing facts.

Recommended investigation sequence:
1. Get the expense details.
2. Get the parsed receipt/supporting-document evidence.
3. Get the applicable published policy rules.
4. Use policy search when you need additional grounded policy context.
5. When enough evidence is available, return the final decision.

You may return only these expense statuses:
- submitted
- information_required
- approved

Use information_required when the expense cannot yet be approved and a specific next action is required.

Required actions:
- none
- additional_information
- additional_document
- manager_decision

Do not approve an expense when required evidence is missing, the applicable policy is unavailable, or the policy requires manager decision.

Do not call tools for side effects. This agent version is investigation-only.

When you have enough evidence, return a JSON object matching the AgentDecision schema with:
status, reason, required_action, evidence (an array of evidence objects), missing_information.
"""

    @staticmethod
    def _tool_definitions() -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_expense",
                    "description": "Retrieve the structured expense request and its existing document/approval associations.",
                    "parameters": {
                        "type": "object",
                        "properties": {"expense_id": {"type": "string"}},
                        "required": ["expense_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_expense_evidence",
                    "description": "Retrieve parsed structured evidence for all documents attached to an expense.",
                    "parameters": {
                        "type": "object",
                        "properties": {"expense_id": {"type": "string"}},
                        "required": ["expense_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_expense_policy",
                    "description": "Retrieve the published policy version applicable to the expense date, including normalized policy rules.",
                    "parameters": {
                        "type": "object",
                        "properties": {"expense_id": {"type": "string"}},
                        "required": ["expense_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_expense_policy",
                    "description": "Search company knowledge for additional grounded expense policy context and return sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

    async def _execute_tool(
        self,
        name: str,
        arguments: str,
        expense_id: str,
    ) -> dict[str, Any]:
        payload = json.loads(arguments or "{}")

        if name == "get_expense":
            return await self.tools.get_expense(payload.get("expense_id", expense_id))
        if name == "get_expense_evidence":
            return await self.tools.get_expense_evidence(payload.get("expense_id", expense_id))
        if name == "get_expense_policy":
            return await self.tools.get_expense_policy(payload.get("expense_id", expense_id))
        if name == "search_expense_policy":
            return await self.tools.search_expense_policy(payload["query"])

        raise ValueError(f"Unknown expense agent tool: {name}")

    @staticmethod
    def _parse_decision(content: str | None) -> AgentDecision:
        if not content:
            raise ValueError("Expense agent returned an empty decision")
        return AgentDecision.model_validate_json(content)
