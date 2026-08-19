import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import app_settings
from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.services import ExpenseService

from .schemas import AgentDecision
from .state import ExpenseAgentState
from app.plugins.expenses.tools import ExpenseAgentTools


class ExpenseAgent:
    MAX_TOOL_ROUNDS = 6

    def __init__(
        self,
        expense_service: ExpenseService,
        knowledge_service: KnowledgeService,
        client: AsyncOpenAI | None = None,
        model: str | None = None,
    ) -> None:
        self.tools = ExpenseAgentTools(expense_service, knowledge_service)
        self.client = client or AsyncOpenAI(api_key=app_settings.openai_api_key)
        self.model = model or app_settings.rag_llm_model

    async def resolve(self, expense_id: str) -> AgentDecision:
        expense = await self.tools.expense_service.get_by_business_id(expense_id)
        state = ExpenseAgentState(expense=expense)

        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": self._system_prompt(),
            },
            {
                "role": "user",
                "content": f"Resolve expense {expense_id} according to company policy.",
            },
        ]

        for _ in range(self.MAX_TOOL_ROUNDS):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._tool_definitions(),
                tool_choice="auto",
                temperature=0,
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls or []

            messages.append(message.model_dump(exclude_none=True))

            if not tool_calls:
                decision = self._parse_decision(message.content)
                state.tool_results.extend(
                    [
                        {
                            "type": "final_decision",
                            "status": decision.status.value,
                        }
                    ]
                )
                return decision

            for tool_call in tool_calls:
                result = await self._execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    expense_id,
                )
                state.tool_results.append(
                    {
                        "tool": tool_call.function.name,
                        "result": result,
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        raise RuntimeError("Expense agent exceeded the maximum tool-call rounds.")

    @staticmethod
    def _system_prompt() -> str:
        return """You are the Expense Resolution Agent.

Your goal is to resolve an expense according to company policy.

You may investigate using the provided read-only tools. Decide what information you need and which tool to call. Do not invent policy rules or missing facts.

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

Do not approve an expense merely because the user supplied an amount. Use policy evidence when a policy decision is required.

Do not call tools for side effects. This agent version is investigation-only.

When you have enough evidence, return a JSON object matching the AgentDecision schema with:
status, reason, required_action, evidence, missing_information.
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
                        "properties": {
                            "expense_id": {"type": "string"},
                        },
                        "required": ["expense_id"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_expense_policy",
                    "description": "Search company knowledge for expense reimbursement policies and return grounded sources.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                        },
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

        if name == "search_expense_policy":
            return await self.tools.search_expense_policy(payload["query"])

        raise ValueError(f"Unknown expense agent tool: {name}")

    @staticmethod
    def _parse_decision(content: str | None) -> AgentDecision:
        if not content:
            raise ValueError("Expense agent returned an empty decision")
        return AgentDecision.model_validate_json(content)
