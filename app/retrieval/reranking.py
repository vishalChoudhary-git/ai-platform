from abc import ABC, abstractmethod

from app.retrieval.schemas import RetrievedChunk


class Reranker(ABC):
    @abstractmethod
    async def rerank(
        self,
        query: str,
        candidates: list[RetrievedChunk],
        top_k: int,
    ) -> list[RetrievedChunk]:
        """Rank candidates by query relevance."""
        raise NotImplementedError

