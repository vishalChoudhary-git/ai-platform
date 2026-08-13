from app.retrieval.schemas import RetrievedChunk


class RerankedRetrievedChunk(RetrievedChunk):
    rerank_score: float | None = None
    rerank_rank: int | None = None
