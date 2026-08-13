from fastapi import APIRouter, Depends

from app.retrieval.api.dependencies import get_retrieval_service
from app.retrieval.schemas import (
    KeywordSearchRequest,
    KeywordSearchResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.retrieval.services import RetrievalService

router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


@router.post(
    "/search",
    response_model=RetrievalResponse,
)
async def search(
    request: RetrievalRequest,
    service: RetrievalService = Depends(
        get_retrieval_service,
    ),
) -> RetrievalResponse:
    return await service.retrieve(request)


@router.post(
    "/keyword-search",
    response_model=KeywordSearchResponse,
)
async def keyword_search(
    request: KeywordSearchRequest,
    service: RetrievalService = Depends(
        get_retrieval_service,
    ),
) -> KeywordSearchResponse:
    return await service.keyword_search(request)
