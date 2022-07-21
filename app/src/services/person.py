from functools import lru_cache, partial
from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.models import Person, Film
from src.services.base_service import BaseSearcher, get_base_searcher


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, searcher: BaseSearcher, index_name: str):
        self.redis = redis
        self.elastic = elastic
        self.searcher = searcher
        self.index_name = index_name

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.searcher.get_by_id(person_id, self.index_name, Person)
        return person

    async def get_person_films(self, person_id: str) -> Optional[list[Film]]:
        return

    async def search_person(
            self,
            size: int = 50,
            offset: Union[int, None] = None,
            query: Union[str, None] = None
    ) -> Optional[tuple[list[Person], int]]:

        es_search = partial(
            self.elastic.search,
            index=self.index_name,
            size=size,
            from_=offset,
            rest_total_hits_as_int=True,
        )
        if query:
            search_query = {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"full_name": query}}
                        ]
                    }
                }
            }
            search_result = await es_search(body=search_query)
        else:
            search_result = await es_search()

        found = search_result['hits']['total']
        docs = search_result['hits'].get('hits')
        if docs:
            return [Person.parse_obj(doc['_source']) for doc in docs], found
        return [], found


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
        searcher: BaseSearcher = Depends(get_base_searcher),
) -> PersonService:
    return PersonService(redis, elastic, searcher, index_name='persons')
