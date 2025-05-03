from redis.asyncio import Redis


class RedisClient:
    @classmethod
    async def get_db_count(cls, *, conn: Redis) -> int:
        config = await conn.config_get("databases")
        return int(config["databases"])
