from collections.abc import Sequence
from uuid import UUID

from ai_document_intelligence.embeddings import EmbeddingProvider

from app.retrieval.repositories import RetrievalRepository
from app.retrieval.reranking import Reranker
from app.retrieval.schemas import RetrievedChunk


class RetrievalService:
    RRF_K = 60

    def __init__(
        self,
        repository: RetrievalRepository,
        embedding_provider: EmbeddingProvider,
        reranker: Reranker | None = None,
    ):
        self.repository = repository
        self.embedding_provider = embedding_provider
        self.reranker = reranker

    async def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        min_similarity: float = 0.3,
    ) -> list[RetrievedChunk]:
        query = self._validate_query(query)
        query_embedding = self.embedding_provider.embed(query)

        rows = await self.repository.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            min_similarity=min_similarity,
        )

        results = []
        for rank, row in enumerate(rows, start=1):
            result = self._map_row(row)
            result.vector_similarity = float(row.similarity)
            result.vector_rank = rank
            results.append(result)

        return results

    async def keyword_search(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        query = self._validate_query(query)

        rows = await self.repository.keyword_search(
            query=query,
            top_k=top_k,
        )

        results = []
        for rank, row in enumerate(rows, start=1):
            result = self._map_row(row)
            result.keyword_score = float(row.score)
            result.keyword_rank = rank
            results.append(result)

        return results

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 20,
        vector_top_k: int = 20,
        keyword_top_k: int = 20,
        min_similarity: float = 0.3,
    ) -> list[RetrievedChunk]:
        vector_results = await self.semantic_search(
            query=query,
            top_k=vector_top_k,
            min_similarity=min_similarity,
        )

        keyword_results = await self.keyword_search(
            query=query,
            top_k=keyword_top_k,
        )

        return self._fuse_with_rrf(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k,
        )

    async def retrieve(
        self,
        query: str,
        candidate_top_k: int = 20,
        final_top_k: int = 5,
        min_similarity: float = 0.3,
    ) -> list[RetrievedChunk]:
        candidates = await self.hybrid_search(
            query=query,
            top_k=candidate_top_k,
            vector_top_k=candidate_top_k,
            keyword_top_k=candidate_top_k,
            min_similarity=min_similarity,
        )

        if self.reranker is None:
            return candidates[:final_top_k]

        return await self.reranker.rerank(
            query=query,
            candidates=candidates,
            top_k=final_top_k,
        )

    def _fuse_with_rrf(
        self,
        vector_results: Sequence[RetrievedChunk],
        keyword_results: Sequence[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        candidates: dict[UUID, RetrievedChunk] = {}

        for rank, result in enumerate(vector_results, start=1):
            result.vector_rank = rank
            result.rrf_score = 1 / (self.RRF_K + rank)
            candidates[result.chunk_id] = result

        for rank, result in enumerate(keyword_results, start=1):
            existing = candidates.get(result.chunk_id)

            if existing is None:
                result.keyword_rank = rank
                result.rrf_score = 1 / (self.RRF_K + rank)
                candidates[result.chunk_id] = result
                continue

            existing.keyword_rank = rank
            existing.keyword_score = result.keyword_score
            existing.rrf_score = (existing.rrf_score or 0.0) + 1 / (self.RRF_K + rank)

        return sorted(
            candidates.values(),
            key=lambda result: result.rrf_score or 0.0,
            reverse=True,
        )[:top_k]

    @staticmethod
    def _validate_query(query: str) -> str:
        query = query.strip()
        if not query:
            raise ValueError("query must not be empty")
        return query

    @staticmethod
    def _map_row(row) -> RetrievedChunk:
        return RetrievedChunk(
            chunk_id=row.id,
            document_id=row.document_id,
            text=row.text,
            page_number=row.page_number,
            chunk_index=row.chunk_index,
            metadata=row.metadata_,
        )
