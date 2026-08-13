from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.rag.context_builder import ContextBuilder
from app.rag.schemas import RAGResponse
from app.rag.service import RAGService
from app.retrieval.schemas import RetrievedChunk


def make_chunk(text: str, index: int = 0) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        text=text,
        page_number=1,
        chunk_index=index,
    )


def test_context_builder_numbers_sources() -> None:
    builder = ContextBuilder()

    chunks = [
        make_chunk("Hotel limit is 180 dollars."),
        make_chunk("Meals are reimbursable."),
    ]

    context = builder.build(chunks)

    assert "SOURCE [1]" in context
    assert "SOURCE [2]" in context
    assert "Hotel limit is 180 dollars." in context
    assert "Meals are reimbursable." in context


@pytest.mark.asyncio
async def test_rag_service_builds_answer_and_sources() -> None:
    retrieval = Mock()
    retrieval.retrieve = AsyncMock(
        return_value=[
            make_chunk("Hotel reimbursement is capped at 180 dollars.", 2),
        ]
    )

    llm = Mock()
    llm.generate = AsyncMock(return_value="The hotel reimbursement limit is $180 per night. [1]")

    service = RAGService(
        retrieval_service=retrieval,
        context_builder=ContextBuilder(),
        llm_generator=llm,
    )

    response = await service.answer("What is the hotel reimbursement limit?")

    assert isinstance(response, RAGResponse)
    assert "$180" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].source_index == 1

    retrieval.retrieve.assert_awaited_once()
    llm.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_rag_service_returns_no_source_answer_when_retrieval_is_empty() -> None:
    retrieval = Mock()
    retrieval.retrieve = AsyncMock(return_value=[])

    llm = Mock()
    llm.generate = AsyncMock()

    service = RAGService(
        retrieval_service=retrieval,
        context_builder=ContextBuilder(),
        llm_generator=llm,
    )

    response = await service.answer("Unknown question")

    assert response.sources == []
    assert "not found" in response.answer
    llm.generate.assert_not_awaited()
