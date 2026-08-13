import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.retrieval.schemas import RetrievedChunk
from app.retrieval.services import RetrievalService


class FakeEmbeddingProvider:
    def __init__(self):
        self.queries: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.queries.append(text)
        return [0.1, 0.2, 0.3]


class FakeRetrievalRepository:
    def __init__(self, vector_rows=None, keyword_rows=None):
        self.vector_rows = vector_rows or []
        self.keyword_rows = keyword_rows or []
        self.query_embedding = None
        self.vector_top_k = None
        self.min_similarity = None
        self.keyword_query = None
        self.keyword_top_k = None

    async def similarity_search(
        self,
        query_embedding,
        top_k,
        min_similarity,
    ):
        self.query_embedding = query_embedding
        self.vector_top_k = top_k
        self.min_similarity = min_similarity
        return self.vector_rows

    async def keyword_search(self, query, top_k):
        self.keyword_query = query
        self.keyword_top_k = top_k
        return self.keyword_rows


def make_row(
    *,
    chunk_id=None,
    document_id=None,
    text="Example chunk",
    similarity=0.82,
    score=0.91,
):
    return SimpleNamespace(
        id=chunk_id or uuid4(),
        document_id=document_id or uuid4(),
        text=text,
        page_number=1,
        chunk_index=0,
        metadata_={},
        similarity=similarity,
        score=score,
    )


def test_semantic_search_embeds_query_and_applies_configuration():
    row = make_row(similarity=0.82)
    repository = FakeRetrievalRepository(vector_rows=[row])
    embedding_provider = FakeEmbeddingProvider()
    service = RetrievalService(repository, embedding_provider)

    results = asyncio.run(
        service.semantic_search(
            query="  revenue  ",
            top_k=5,
            min_similarity=0.3,
        )
    )

    assert embedding_provider.queries == ["revenue"]
    assert repository.query_embedding == [0.1, 0.2, 0.3]
    assert repository.vector_top_k == 5
    assert repository.min_similarity == 0.3
    assert results[0].chunk_id == row.id
    assert results[0].vector_rank == 1
    assert results[0].vector_similarity == 0.82


def test_keyword_search_does_not_use_embeddings():
    row = make_row(score=0.91)
    repository = FakeRetrievalRepository(keyword_rows=[row])
    embedding_provider = FakeEmbeddingProvider()
    service = RetrievalService(repository, embedding_provider)

    results = asyncio.run(
        service.keyword_search(
            query="  hotel reimbursement  ",
            top_k=3,
        )
    )

    assert embedding_provider.queries == []
    assert repository.keyword_query == "hotel reimbursement"
    assert repository.keyword_top_k == 3
    assert results[0].chunk_id == row.id
    assert results[0].keyword_rank == 1
    assert results[0].keyword_score == 0.91


def test_hybrid_search_combines_rankings_with_rrf():
    shared_chunk_id = uuid4()
    vector_only_id = uuid4()
    keyword_only_id = uuid4()

    vector_shared = make_row(
        chunk_id=shared_chunk_id,
        text="Shared result",
        similarity=0.9,
    )
    vector_only = make_row(
        chunk_id=vector_only_id,
        text="Vector result",
        similarity=0.8,
    )
    keyword_shared = make_row(
        chunk_id=shared_chunk_id,
        text="Shared result",
        score=0.9,
    )
    keyword_only = make_row(
        chunk_id=keyword_only_id,
        text="Keyword result",
        score=0.8,
    )

    repository = FakeRetrievalRepository(
        vector_rows=[vector_shared, vector_only],
        keyword_rows=[keyword_shared, keyword_only],
    )
    service = RetrievalService(
        repository,
        FakeEmbeddingProvider(),
    )

    results = asyncio.run(
        service.hybrid_search(
            query="hotel reimbursement",
            top_k=3,
            vector_top_k=2,
            keyword_top_k=2,
        )
    )

    assert len(results) == 3
    assert results[0].chunk_id == shared_chunk_id
    assert results[0].vector_rank == 1
    assert results[0].keyword_rank == 1
    assert results[0].rrf_score > results[1].rrf_score
    assert results[1].chunk_id == vector_only_id


def test_search_rejects_blank_query():
    service = RetrievalService(
        FakeRetrievalRepository(),
        FakeEmbeddingProvider(),
    )

    with pytest.raises(ValueError, match="query must not be empty"):
        asyncio.run(service.semantic_search("   "))

    with pytest.raises(ValueError, match="query must not be empty"):
        asyncio.run(service.keyword_search("   "))


def test_rrf_uses_expected_constant():
    assert RetrievalService.RRF_K == 60
