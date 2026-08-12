from sqlalchemy.ext.asyncio import AsyncSession

from app.features.documents.models import DocumentChunk


class DocumentChunkRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create_many(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        self.session.add_all(chunks)

        await self.session.flush()
