from collections.abc import Sequence

from sqlalchemy import func, select
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

    async def keyword_search(
        self,
        query: str,
        top_k: int,
    ) -> Sequence[Row]:
        search_vector = func.to_tsvector("english", DocumentChunk.text)
        search_query = func.plainto_tsquery("english", query)
        score = func.ts_rank(search_vector, search_query).label("score")

        statement = (
            select(
                DocumentChunk.id,
                DocumentChunk.document_id,
                DocumentChunk.text,
                DocumentChunk.page_number,
                DocumentChunk.chunk_index,
                DocumentChunk.metadata_,
                score,
            )
            .where(search_vector.op("@@")(search_query))
            .order_by(score.desc())
            .limit(top_k)
        )

        result = await self.session.execute(statement)

        return result.all()
