from typing import Optional

import orjson
from pydantic import BaseModel

from src.models.film import orjson_dumps


class UUIDBaseClass(BaseModel):
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Pagination(BaseModel):
    found: int
    pages: int
    per_page: int
    page: int


class Person(UUIDBaseClass):
    name: str


class Genre(UUIDBaseClass):
    name: str


class FilmBase(UUIDBaseClass):
    title: str
    description: str
    imdb_rating: float


class Film(FilmBase):
    genre: list[str]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[list[str]]


class Films(BaseModel):
    meta: Pagination
    data: list[FilmBase]
