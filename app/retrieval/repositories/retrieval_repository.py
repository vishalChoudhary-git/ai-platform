from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.documents.models import DocumentChunk


class RetrievalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int,
        min_similarity: float,
    ) -> Sequence[Row]:
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding,
        )

        similarity = (1 - distance).label("similarity")

        statement = (
            select(
                DocumentChunk.id,
                DocumentChunk.document_id,
                DocumentChunk.text,
                DocumentChunk.page_number,
                DocumentChunk.chunk_index,
                DocumentChunk.metadata_,
                similarity,
            )
            .where(
                DocumentChunk.embedding.is_not(None),
                (1 - distance) >= min_similarity,
            )
            .order_by(distance)
            .limit(top_k)
        )

        result = await self.session.execute(statement)

        return result.all()
