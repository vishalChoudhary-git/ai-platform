from datetime import datetime, timezone
import json
import logging
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.features.documents.models.document_chunk import DocumentChunk

from .cache import ExpensePolicyCache
from .enums import ExpensePolicyStatus
from .models import ExpensePolicy
from .schemas import ExpensePolicySnapshot, PolicyRule

logger = logging.getLogger(__name__)


class ExpensePolicyProcessor:
    def __init__(
        self,
        session: AsyncSession,
        cache: ExpensePolicyCache,
        client: AsyncOpenAI | None = None,
        model: str | None = None,
    ) -> None:
        settings = get_settings()
        self.session = session
        self.cache = cache
        self.client = client or AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.rag_llm_model

    async def process(self, policy_id: str) -> ExpensePolicySnapshot:
        policy = await self.session.scalar(
            select(ExpensePolicy).where(ExpensePolicy.policy_id == policy_id)
        )
        if policy is None:
            raise ValueError(f"Expense policy '{policy_id}' was not found.")

        logger.info(
            "ExpensePolicyProcessor.process: start policy_id=%s version=%s checksum=%s",
            policy.policy_id,
            policy.version,
            policy.checksum,
        )

        await self._set_status(policy.id, ExpensePolicyStatus.PROCESSING)

        try:
            result = await self.session.scalars(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == policy.document_id)
                .order_by(DocumentChunk.chunk_index.asc())
            )
            texts = [chunk.text for chunk in result]
            if not texts:
                raise ValueError("Policy document has no parsed chunks.")

            parsed_text = "\n\n".join(texts)
            rules = await self._extract_rules(parsed_text)
            snapshot = ExpensePolicySnapshot(
                policy_id=policy.policy_id,
                version=policy.version,
                checksum=policy.checksum,
                effective_from=(
                    policy.effective_from.isoformat()
                    if policy.effective_from
                    else None
                ),
                rules=rules,
            )

            await self.cache.set(snapshot)
            await self._set_published(policy.id)

            logger.info(
                "ExpensePolicyProcessor.process: published policy_id=%s rules=%s",
                policy.policy_id,
                len(rules),
            )
            return snapshot
        except Exception:
            await self._set_status(policy.id, ExpensePolicyStatus.UPLOADED)
            logger.exception(
                "ExpensePolicyProcessor.process: failed policy_id=%s",
                policy.policy_id,
            )
            raise

    async def _extract_rules(self, text: str) -> list[PolicyRule]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract company expense policy rules from the supplied text. "
                        "Return JSON only with a top-level 'rules' array. "
                        "Each rule must contain rule_id, category, condition, action, "
                        "and parameters. Never invent a rule not supported by the text."
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Policy rule extraction returned empty output.")

        payload: dict[str, Any] = json.loads(content)
        return [PolicyRule.model_validate(item) for item in payload.get("rules", [])]

    async def _set_status(
        self,
        policy_db_id: UUID,
        status: ExpensePolicyStatus,
    ) -> None:
        await self.session.execute(
            update(ExpensePolicy)
            .where(ExpensePolicy.id == policy_db_id)
            .values(status=status)
        )
        await self.session.commit()

    async def _set_published(self, policy_db_id: UUID) -> None:
        await self.session.execute(
            update(ExpensePolicy)
            .where(ExpensePolicy.id == policy_db_id)
            .values(
                status=ExpensePolicyStatus.PUBLISHED,
                published_at=datetime.now(timezone.utc),
            )
        )
        await self.session.commit()
