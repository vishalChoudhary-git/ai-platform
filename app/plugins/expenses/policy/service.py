from datetime import date
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ingestion.types import RawDocument
from app.features.documents.models.enums import DocumentSource
from app.features.documents.services import DocumentService

from .models import ExpensePolicy


class ExpensePolicyService:
    def __init__(
        self,
        session: AsyncSession,
        document_service: DocumentService,
    ) -> None:
        self.session = session
        self.document_service = document_service

    async def create(
        self,
        *,
        policy_name: str,
        version: str,
        effective_from: date | None,
        published_by: str,
        content: bytes,
        filename: str,
        mime_type: str,
    ) -> ExpensePolicy:
        existing = await self.session.scalar(
            select(ExpensePolicy).where(
                ExpensePolicy.policy_name == policy_name,
                ExpensePolicy.version == version,
            )
        )
        if existing:
            raise ValueError("A policy with the same name and version already exists.")

        document = await self.document_service.ingest(
            RawDocument(
                content=content,
                filename=filename,
                mime_type=mime_type,
                source=DocumentSource.UPLOAD,
                metadata={"domain": "expense_policy"},
            )
        )

        existing_document_policy = await self.session.scalar(
            select(ExpensePolicy).where(ExpensePolicy.document_id == document.id)
        )
        if existing_document_policy:
            raise ValueError("A policy for this document already exists.")

        policy = ExpensePolicy(
            policy_id=f"POL-{uuid4().hex[:20].upper()}",
            policy_name=policy_name,
            version=version,
            document_id=document.id,
            checksum=document.checksum,
            effective_from=effective_from,
            published_by=published_by,
        )
        self.session.add(policy)
        await self.session.commit()
        await self.session.refresh(policy)
        return policy
