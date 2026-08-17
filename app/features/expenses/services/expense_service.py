from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.features.documents.models import Document
from app.features.expenses.models import Expense, ExpenseDocument
from app.features.expenses.schemas import ExpenseCreateRequest


class ExpenseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, request: ExpenseCreateRequest) -> Expense:
        document_ids = list(dict.fromkeys(request.document_ids))
        documents = await self._get_documents(document_ids)

        if len(documents) != len(document_ids):
            found = {document.id for document in documents}
            missing = [str(document_id) for document_id in document_ids if document_id not in found]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "One or more documents were not found.", "document_ids": missing},
            )

        generated_id = f"EXP-{uuid4().hex[:12].upper()}"
        expense = Expense(
            expense_id=generated_id,
            employee_name=request.employee_name,
            employee_email=request.employee_email,
            manager_email=request.manager_email,
            category=request.category,
            description=request.description,
            amount=request.amount,
            currency=request.currency,
            expense_date=request.expense_date,
            documents=[ExpenseDocument(document_id=document_id) for document_id in document_ids],
        )

        self.session.add(expense)
        await self.session.commit()
        return await self.get_by_id(expense.id)

    async def get_by_id(self, expense_id: UUID) -> Expense:
        result = await self.session.execute(
            select(Expense)
            .options(selectinload(Expense.documents))
            .where(Expense.id == expense_id)
        )
        expense = result.scalar_one_or_none()
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
        return expense

    async def _get_documents(self, document_ids: list[UUID]) -> list[Document]:
        result = await self.session.execute(
            select(Document).where(Document.id.in_(document_ids))
        )
        return list(result.scalars().all())
