from io import BytesIO
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import Headers

from app.core.ingestion.types import RawDocument
from app.features.documents.models.document import Document
from app.features.documents.services import DocumentService
from app.plugins.expenses.models import Expense, ExpenseDocument
from app.plugins.expenses.services import ExpenseService


class FakeSession:
    def __init__(self) -> None:
        self.added: list[ExpenseDocument] = []

    def add(self, value: ExpenseDocument) -> None:
        self.added.append(value)

    async def execute(self, _query):
        return SimpleNamespace(scalar_one_or_none=lambda: None)


class FakeDocumentService:
    def __init__(self) -> None:
        self.raw_documents: list[RawDocument] = []

    async def ingest(self, raw_document: RawDocument) -> Document:
        self.raw_documents.append(raw_document)
        return cast(Document, SimpleNamespace(id=uuid4()))


def make_upload_file() -> UploadFile:
    return UploadFile(
        file=BytesIO(b"fake pdf content"),
        filename="hotel-receipt.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )


@pytest.mark.asyncio
async def test_attach_new_documents_does_not_store_expense_id_in_document_metadata() -> None:
    session = FakeSession()
    document_service = FakeDocumentService()
    service = ExpenseService(
        session=cast(AsyncSession, session),
        document_service=cast(DocumentService, document_service),
    )
    expense = cast(Expense, SimpleNamespace(id=uuid4(), expense_id="EXP-001"))

    await service._attach_new_documents(expense, [make_upload_file()])

    assert document_service.raw_documents[0].metadata == {}
    assert len(session.added) == 1
    assert session.added[0].expense_id == expense.id
