import json

from redis.asyncio import Redis

from .schemas import ExpensePolicySnapshot


class ExpensePolicyCache:
    PREFIX = "expense:policy:"

    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def key(cls, checksum: str) -> str:
        return f"{cls.PREFIX}{checksum}"

    async def get(self, checksum: str) -> ExpensePolicySnapshot | None:
        value = await self.redis.get(self.key(checksum))
        if value is None:
            return None
        return ExpensePolicySnapshot.model_validate_json(value)

    async def set(self, snapshot: ExpensePolicySnapshot) -> None:
        await self.redis.set(
            self.key(snapshot.checksum),
            snapshot.model_dump_json(),
        )

    async def delete(self, checksum: str) -> None:
        await self.redis.delete(self.key(checksum))

    async def ping(self) -> bool:
        return bool(await self.redis.ping())
