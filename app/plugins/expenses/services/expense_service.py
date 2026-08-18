from collections.abc import Sequence
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.ingestion.types import RawDocument
from app.features.documents.models.enums import DocumentSource
from app.features.documents.services import DocumentService
from app.plugins.expenses.models import (
    Expense,
    ExpenseDocument,
    ExpenseDocumentRole,
    ExpenseRequiredAction,
    ExpenseStatus,
)
from app.plugins.expenses.schemas import ExpenseCreateData, ExpenseUpdateData


class ExpenseService:
    def __init__(self, session: AsyncSession, document_service: DocumentService):
        self.session = session
        self.document_service = document_service

    async def create(
        self,
        data: ExpenseCreateData,
        files: Sequence[UploadFile],
    ) -> tuple[Expense, list[UUID]]:
        if not files:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one supporting document is required.",
            )

        expense = Expense(
            expense_id=f"EXP-{uuid4().hex[:12].upper()}",
            employee_name=data.employee_name,
            employee_email=data.employee_email,
            manager_email=data.manager_email,
            category=data.category,
            description=data.description,
            amount=data.amount,
            currency=data.currency,
            expense_date=data.expense_date,
        )
        self.session.add(expense)
        await self.session.flush()

        document_ids = await self._attach_new_documents(expense, files)
        await self.session.commit()
        return await self.get_by_id(expense.id), document_ids

    async def append(
        self,
        expense_id: str,
        files: Sequence[UploadFile],
        data: ExpenseUpdateData | None = None,
    ) -> tuple[Expense, list[UUID]]:
        expense = await self.get_by_business_id(expense_id)

        if expense.status == ExpenseStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Approved expenses cannot be modified.",
            )

        if not files and data is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Provide additional information or at least one document.",
            )

        if data is not None:
            self._apply_updates(expense, data)

        document_ids = await self._attach_new_documents(expense, files)
        expense.status = ExpenseStatus.SUBMITTED
        expense.decision_reason = None
        expense.required_action = ExpenseRequiredAction.NONE
        expense.decision_evidence = None

        await self.session.commit()
        return await self.get_by_id(expense.id), document_ids

    async def get_by_id(self, expense_id: UUID) -> Expense:
        result = await self.session.execute(
            select(Expense)
            .options(selectinload(Expense.documents), selectinload(Expense.approvals))
            .where(Expense.id == expense_id)
        )
        expense = result.scalar_one_or_none()
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
        return expense

    async def get_by_business_id(self, expense_id: str) -> Expense:
        result = await self.session.execute(
            select(Expense)
            .options(selectinload(Expense.documents), selectinload(Expense.approvals))
            .where(Expense.expense_id == expense_id)
        )
        expense = result.scalar_one_or_none()
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
        return expense

    async def _attach_new_documents(
        self,
        expense: Expense,
        files: Sequence[UploadFile],
    ) -> list[UUID]:
        document_ids: list[UUID] = []
        for file in files:
            document = await self.document_service.ingest(
                RawDocument(
                    content=await file.read(),
                    filename=file.filename,
                    mime_type=file.content_type or "application/octet-stream",
                    source=DocumentSource.UPLOAD,
                    metadata={"expense_id": expense.expense_id},
                )
            )
            if await self._document_already_attached(expense.id, document.id):
                continue
            expense.documents.append(
                ExpenseDocument(
                    document_id=document.id,
                    role=ExpenseDocumentRole.RECEIPT,
                )
            )
            document_ids.append(document.id)
        return document_ids

    async def _document_already_attached(self, expense_id: UUID, document_id: UUID) -> bool:
        result = await self.session.execute(
            select(ExpenseDocument.id).where(
                ExpenseDocument.expense_id == expense_id,
                ExpenseDocument.document_id == document_id,
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    def _apply_updates(expense: Expense, data: ExpenseUpdateData) -> None:
        for field in data.model_fields_set:
            setattr(expense, field, getattr(data, field))
