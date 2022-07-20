from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.models import Genre
from src.services.base_service import BaseSearcher, get_base_searcher


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, searcher: BaseSearcher, index_name: str):
        self.redis = redis
        self.elastic = elastic
        self.searcher = searcher
        self.index_name = index_name

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self.searcher.get_by_id(genre_id, self.index_name, Genre)
        return genre

    async def get_genres(self) -> Optional[tuple[list[Genre], int]]:
        search_result = await self.elastic.search(
            index='genres',
            rest_total_hits_as_int=True,
        )
        found = search_result['hits']['total']
        docs = search_result['hits'].get('hits')
        if docs:
            return [Genre.parse_obj(doc['_source']) for doc in docs], found
        return [], found


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        searcher: BaseSearcher = Depends(get_base_searcher),
) -> GenreService:
    return GenreService(redis, elastic, searcher, index_name='genres')
