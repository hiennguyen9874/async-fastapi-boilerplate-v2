from redis.asyncio import Redis


class RedisRepositoryBase:
    async def create(self, connection: Redis, key: str, value: str) -> None:
        await connection.set(key, value)

    async def get(self, connection: Redis, key: str) -> str | None:
        return await connection.get(key)

    async def delete(self, connection: Redis, key: str) -> None:
        await connection.delete(key)

    async def set_add(self, connection: Redis, key: str, value: str) -> None:
        await connection.sadd(key, value)

    async def set_adds(self, connection: Redis, key: str, values: list[str]) -> None:
        await connection.sadd(key, *values)

    async def set_is_member(self, connection: Redis, key: str, value: str) -> bool:
        return await connection.sismember(key, value)

    async def set_delete(self, connection: Redis, key: str, value: str) -> None:
        await connection.srem(key, value)
