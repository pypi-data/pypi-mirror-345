import json

from redis.asyncio import Redis  # type: ignore [import]


async def set(client: Redis, name: str, value: str, ex: int) -> bool:
    return await client.set(name, json.dumps(value), ex)


async def delete(client: Redis, name: str) -> int:
    return await client.delete(name)


async def get(client: Redis, name: str):
    res = await client.get(name)
    return res if res is None else json.loads(res)
