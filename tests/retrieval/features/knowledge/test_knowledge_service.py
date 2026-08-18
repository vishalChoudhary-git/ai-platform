from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.features.knowledge.services.knowledge_service import KnowledgeService
from app.rag.schemas import RAGResponse, RAGSource


@pytest.mark.asyncio
async def test_query_delegates_to_rag_and_maps_sources() -> None:
    rag_service = AsyncMock()
    rag_service.answer.return_value = RAGResponse(
        answer="The hotel limit is 180 dollars per night. [1]",
        sources=[
            RAGSource(
                source_index=1,
                chunk_id=uuid4(),
                document_id=uuid4(),
                page_number=1,
                chunk_index=2,
                text="Hotel reimbursement is capped at 180 dollars per night.",
            )
        ],
    )

    service = KnowledgeService(rag_service)

    response = await service.query("What is the hotel reimbursement limit?")

    assert response.answer == "The hotel limit is 180 dollars per night. [1]"
    assert len(response.sources) == 1
    assert response.sources[0].source_index == 1
    assert response.sources[0].page_number == 1
    assert response.sources[0].chunk_index == 2

    rag_service.answer.assert_awaited_once_with(query="What is the hotel reimbursement limit?")


@pytest.mark.asyncio
async def test_query_preserves_no_evidence_response() -> None:
    rag_service = AsyncMock()
    rag_service.answer.return_value = RAGResponse(
        answer="The information was not found in the supplied documents.",
        sources=[],
    )

    service = KnowledgeService(rag_service)

    response = await service.query("What is the maternity leave policy?")

    assert response.answer == ("The information was not found in the supplied documents.")
    assert response.sources == []
