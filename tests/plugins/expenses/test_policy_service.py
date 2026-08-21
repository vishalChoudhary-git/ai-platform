from datetime import date
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ingestion.types import RawDocument
from app.features.documents.services import DocumentService
from app.plugins.expenses.policy.service import ExpensePolicyService


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.committed = False
        self.scalar_results = [None, SimpleNamespace(policy_id="POL-EXISTING")]

    async def scalar(self, _query):
        return self.scalar_results.pop(0)

    def add(self, value) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.committed = True


class FakeDocumentService:
    async def ingest(self, raw_document: RawDocument):
        return SimpleNamespace(id=uuid4(), checksum="a" * 64)


@pytest.mark.asyncio
async def test_create_rejects_document_already_attached_to_policy() -> None:
    session = FakeSession()
    service = ExpensePolicyService(
        session=cast(AsyncSession, session),
        document_service=cast(DocumentService, FakeDocumentService()),
    )

    with pytest.raises(ValueError, match="document already exists"):
        await service.create(
            policy_name="Travel Policy",
            version="2026.1",
            effective_from=date(2026, 1, 1),
            published_by="hr@example.com",
            content=b"policy content",
            filename="policy.pdf",
            mime_type="application/pdf",
        )

    assert session.added == []
    assert session.committed is False
