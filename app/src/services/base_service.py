from functools import lru_cache
from typing import Optional, Any

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import BaseModel

from src.core.config import CACHE_EXPIRE_IN_SECONDS
from src.db.elastic import get_elastic
from src.db.redis import get_redis


class BaseSearcher:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, item_id: str, index_name: str, model: Any) -> Optional[BaseModel]:
        item = await self._get_from_cache(item_id, model)
        if not item:
            item = await self._get_from_elastic(item_id, index_name, model)
            if not item:
                return None
            await self._put_to_cache(item)

        return item

    async def _get_from_elastic(self, item_id: str, index_name: str, model: BaseModel) -> Optional[BaseModel]:
        try:
            doc = await self.elastic.get(index_name, item_id)
        except NotFoundError:
            return None
        return model.parse_obj(doc['_source'])

    async def _get_from_cache(self, item_id: str, model: BaseModel) -> Optional[BaseModel]:
        data = await self.redis.get(item_id)
        if not data:
            return None

        item = model.parse_raw(data)
        return item

    async def _put_to_cache(self, item: BaseModel):
        await self.redis.set(item.id, item.json(), expire=CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_base_searcher(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> BaseSearcher:
    return BaseSearcher(redis, elastic)
