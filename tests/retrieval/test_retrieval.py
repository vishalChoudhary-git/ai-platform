import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.retrieval.schemas import RetrievalRequest
from app.retrieval.services import RetrievalService


class FakeEmbeddingProvider:
    def __init__(self):
        self.queries: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.queries.append(text)
        return [0.1, 0.2, 0.3]


class FakeRetrievalRepository:
    def __init__(self, rows):
        self.rows = rows
        self.query_embedding = None
        self.top_k = None
        self.min_similarity = None

    async def similarity_search(
        self,
        query_embedding,
        top_k,
        min_similarity,
    ):
        self.query_embedding = query_embedding
        self.top_k = top_k
        self.min_similarity = min_similarity
        return self.rows


def test_retrieval_request_rejects_blank_query():
    with pytest.raises(ValueError):
        RetrievalRequest(query="   ")


def test_retrieval_request_strips_query():
    request = RetrievalRequest(query="  revenue  ")

    assert request.query == "revenue"


def test_retrieval_request_defaults_similarity_threshold():
    request = RetrievalRequest(query="revenue")

    assert request.min_similarity == 0.3


def test_retrieval_request_rejects_invalid_similarity_threshold():
    with pytest.raises(ValueError):
        RetrievalRequest(query="revenue", min_similarity=1.1)


def test_retrieval_service_embeds_query_and_maps_results():
    chunk_id = uuid4()
    document_id = uuid4()
    rows = [
        SimpleNamespace(
            id=chunk_id,
            document_id=document_id,
            text="Revenue was 180 million dollars.",
            page_number=2,
            chunk_index=3,
            metadata_={"sdk_chunk_id": "doc-chunk-3"},
            similarity=0.82,
        )
    ]

    repository = FakeRetrievalRepository(rows)
    embedding_provider = FakeEmbeddingProvider()
    service = RetrievalService(repository, embedding_provider)

    response = asyncio.run(
        service.retrieve(
            RetrievalRequest(query="  revenue  ", top_k=5),
        )
    )

    assert embedding_provider.queries == ["revenue"]
    assert repository.query_embedding == [0.1, 0.2, 0.3]
    assert repository.top_k == 5
    assert repository.min_similarity == 0.3
    assert len(response.results) == 1
    assert response.results[0].chunk_id == chunk_id
    assert response.results[0].document_id == document_id
    assert response.results[0].text == "Revenue was 180 million dollars."
    assert response.results[0].similarity == 0.82
