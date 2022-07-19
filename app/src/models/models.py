from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class UUIDBaseClass(BaseModel):
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(UUIDBaseClass):
    name: str


class Genre(UUIDBaseClass):
    name: str


class Film(UUIDBaseClass):
    title: str
    description: str
    imdb_rating: float
    genre: list[str]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[list[str]]
