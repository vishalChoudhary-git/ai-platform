from fastapi import APIRouter, Depends

from app.features.knowledge.api.dependencies import get_knowledge_service
from app.features.knowledge.schemas import KnowledgeQueryRequest, KnowledgeQueryResponse
from app.features.knowledge.services import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    request: KnowledgeQueryRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeQueryResponse:
    return await service.query(request.query)
