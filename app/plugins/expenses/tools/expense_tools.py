from typing import Any
from uuid import UUID

from app.features.knowledge.services import KnowledgeService
from app.plugins.expenses.services import ExpenseService


class ExpenseAgentTools:
    def __init__(
        self,
        expense_service: ExpenseService,
        knowledge_service: KnowledgeService,
    ) -> None:
        self.expense_service = expense_service
        self.knowledge_service = knowledge_service

    async def get_expense(self, expense_id: str) -> dict[str, Any]:
        expense = await self.expense_service.get_by_business_id(expense_id)
        return {
            "expense_id": expense.expense_id,
            "employee_name": expense.employee_name,
            "employee_email": expense.employee_email,
            "manager_email": expense.manager_email,
            "category": expense.category,
            "description": expense.description,
            "amount": str(expense.amount) if expense.amount is not None else None,
            "currency": expense.currency,
            "expense_date": expense.expense_date.isoformat() if expense.expense_date else None,
            "status": expense.status.value,
            "documents": [
                {
                    "document_id": str(document.document_id),
                    "role": document.role.value,
                }
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

    async def search_expense_policy(self, query: str) -> dict[str, Any]:
        response = await self.knowledge_service.query(query=query)
        return {
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
