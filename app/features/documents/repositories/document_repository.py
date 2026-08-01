from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.documents.models.document import Document
from app.features.documents.models.enums import DocumentStatus


class DocumentRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        document: Document,
    ) -> Document:
        self.session.add(document)

        await self.session.commit()

        await self.session.refresh(document)

        return document

    async def get_by_checksum(
        self,
        checksum: str,
    ) -> Document | None:
        stmt = select(Document).where(Document.checksum == checksum)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        document_id: UUID,
    ) -> Document | None:
        stmt = select(Document).where(Document.id == document_id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def list(
        self,
    ) -> list[Document]:
        stmt = select(Document)

        result = await self.session.execute(stmt)

        return list(result.scalars().all())

    async def delete(
        self,
        document: Document,
    ) -> None:
        await self.session.delete(document)

        await self.session.commit()

    async def update_status(
        self,
        document_id: UUID,
        status: DocumentStatus,
    ) -> None:
        stmt = update(Document).where(Document.id == document_id).values(status=status)

        await self.session.execute(stmt)

        await self.session.commit()
