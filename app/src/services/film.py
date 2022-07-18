from functools import lru_cache, partial
from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

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
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film.parse_obj(doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
