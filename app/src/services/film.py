from functools import lru_cache, partial
from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.models import Film
from src.services.base_service import BaseSearcher, get_base_searcher

# TODO вынести в настройки
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, searcher: BaseSearcher, index_name: str):
        self.redis = redis
        self.elastic = elastic
        self.searcher = searcher
        self.index_name = index_name

    async def get_films(
            self,
            size: int = 50,
            offset: Union[int, None] = None,
            sort_direction: str = 'desc',
            genre: Union[str, None] = None
    ) -> Optional[tuple[list[Film], int]]:

        sort_field = 'imdb_rating'
        es_search = partial(
            self.elastic.search,
            index='movies',
            size=size,
            sort=[f'{sort_field}:{sort_direction}'],
            from_=offset,
            rest_total_hits_as_int=True,
        )
        if genre:
            search_genre = {'query': {'match': {'genre': {
                "query": "Adventure",
                "fuzziness": "auto",
                "operator": "and"
            }}}}
            search_result = await es_search(body=search_genre)
        else:
            search_result = await es_search()

        found = search_result['hits']['total']
        docs = search_result['hits'].get('hits')
        if docs:
            return [Film.parse_obj(doc['_source']) for doc in docs], found
        return [], found

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self.searcher.get_by_id(film_id, self.index_name, Film)
        return film


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        searcher: BaseSearcher = Depends(get_base_searcher),
) -> FilmService:
    return FilmService(redis, elastic, searcher, index_name='movies')
