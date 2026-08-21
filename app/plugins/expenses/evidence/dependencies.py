from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.core.db.session import get_db
from app.features.documents.api.dependencies import get_ingestion_service
from app.features.documents.services import IngestionService

from .service import ExpenseEvidenceProcessor


def get_evidence_processor(
    session: AsyncSession = Depends(get_db),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
    redis: Redis = Depends(get_redis),
) -> ExpenseEvidenceProcessor:
    return ExpenseEvidenceProcessor(
        session=session,
        ingestion_service=ingestion_service,
        redis=redis,
    )
