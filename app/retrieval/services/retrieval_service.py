from ai_document_intelligence.embeddings import EmbeddingProvider

from app.retrieval.repositories import RetrievalRepository
from app.retrieval.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunk,
)


class RetrievalService:
    def __init__(
        self,
        repository: RetrievalRepository,
        embedding_provider: EmbeddingProvider,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResponse:
        query_embedding = self.embedding_provider.embed(
            request.query,
        )

        rows = await self.repository.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            min_similarity=request.min_similarity,
        )

        results = [
            RetrievedChunk(
                chunk_id=row.id,
                document_id=row.document_id,
                text=row.text,
                page_number=row.page_number,
                chunk_index=row.chunk_index,
                metadata=row.metadata_,
                similarity=float(row.similarity),
            )
            for row in rows
        ]

        return RetrievalResponse(
            results=results,
        )
