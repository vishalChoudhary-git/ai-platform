from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.session import get_db
from app.features.knowledge.services import KnowledgeService
from app.rag.factory import create_rag_service


def get_knowledge_service(
    session: AsyncSession = Depends(get_db),
) -> KnowledgeService:
    return KnowledgeService(create_rag_service(session))
