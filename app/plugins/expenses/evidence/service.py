import json
import logging
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.features.documents.models.document_chunk import DocumentChunk
from app.features.documents.services.ingestion_service import IngestionService

from .cache import ExpenseEvidenceCache, ExpenseEvidence

logger = logging.getLogger(__name__)


class ExpenseEvidenceProcessor:
    def __init__(
        self,
        session: AsyncSession,
        ingestion_service: IngestionService,
        redis: Redis,
        client: AsyncOpenAI | None = None,
        model: str | None = None,
    ) -> None:
        settings = get_settings()
        self.session = session
        self.ingestion_service = ingestion_service
        self.cache = ExpenseEvidenceCache(redis)
        self.client = client or AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.rag_llm_model

    async def process(self, expense_id: str, document_id: UUID) -> ExpenseEvidence:
        logger.info(
            "ExpenseEvidenceProcessor.process: start expense_id=%s document_id=%s",
            expense_id,
            document_id,
        )

        await self.ingestion_service.process_document(document_id)

        chunks = await self.session.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        texts = [chunk.text for chunk in chunks]
        if not texts:
            raise ValueError("Expense document has no parsed chunks.")

        parsed_text = "\n\n".join(texts)
        evidence = await self._extract_evidence(expense_id, document_id, parsed_text)
        await self.cache.set(evidence)

        logger.info(
            "ExpenseEvidenceProcessor.process: complete expense_id=%s document_id=%s fields=%s",
            expense_id,
            document_id,
            len(evidence.fields),
        )
        return evidence

    async def _extract_evidence(
        self,
        expense_id: str,
        document_id: UUID,
        text: str,
    ) -> ExpenseEvidence:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract structured expense evidence from the receipt text. "
                        "Return JSON only with document_type, merchant, amount, currency, "
                        "expense_date, and fields. Use null when a value is not supported by "
                        "the receipt. Never invent values."
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Expense evidence extraction returned empty output.")

        payload: dict[str, Any] = json.loads(content)
        return ExpenseEvidence(
            expense_id=expense_id,
            document_id=document_id,
            document_type=payload.get("document_type"),
            merchant=payload.get("merchant"),
            amount=str(payload["amount"]) if payload.get("amount") is not None else None,
            currency=payload.get("currency"),
            expense_date=payload.get("expense_date"),
            fields=payload.get("fields") or {},
        )
