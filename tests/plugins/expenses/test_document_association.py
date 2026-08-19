from types import SimpleNamespace
from uuid import uuid4

from fastapi import UploadFile
from starlette.datastructures import Headers

from app.plugins.expenses.services import ExpenseService


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, value: object) -> None:
        self.added.append(value)


class FakeDocumentService:
    def __init__(self) -> None:
        self.raw_documents = []

    async def ingest(self, raw_document):
        self.raw_documents.append(raw_document)
        return SimpleNamespace(id=uuid4())


def make_upload_file() -> UploadFile:
    return UploadFile(
        filename="hotel-receipt.pdf",
        file=None,
        headers=Headers({"content-type": "application/pdf"}),
    )


async def test_attach_new_documents_does_not_store_expense_id_in_document_metadata() -> None:
    session = FakeSession()
    document_service = FakeDocumentService()
    service = ExpenseService(session=session, document_service=document_service)
    expense = SimpleNamespace(id=uuid4(), expense_id="EXP-001")

    await service._attach_new_documents(expense, [make_upload_file()])

    assert document_service.raw_documents[0].metadata == {}
    assert len(session.added) == 1
    assert session.added[0].expense_id == expense.id
