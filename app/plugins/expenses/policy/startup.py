from sqlalchemy import select

from app.core.cache import get_redis
from app.core.db.session import async_session_factory

from .cache import ExpensePolicyCache
from .enums import ExpensePolicyStatus
from .models import ExpensePolicy
from .processor import ExpensePolicyProcessor


async def warm_expense_policy_cache() -> None:
    async with async_session_factory() as session:
        cache = ExpensePolicyCache(get_redis())
        result = await session.scalars(
            select(ExpensePolicy).where(
                ExpensePolicy.status == ExpensePolicyStatus.PUBLISHED,
            )
        )
        policies = list(result)

        for policy in policies:
            if await cache.get(policy.checksum) is not None:
                continue

            await ExpensePolicyProcessor(
                session=session,
                cache=cache,
            ).process(policy.policy_id)
