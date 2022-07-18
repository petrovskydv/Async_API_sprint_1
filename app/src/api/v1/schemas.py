from typing import Optional

import orjson
from pydantic import BaseModel

from src.models.film import orjson_dumps


class UUIDMixin(BaseModel):
    id: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(UUIDMixin):
    name: str


class Genre(BaseModel):
    name: str


class FilmBase(UUIDMixin):
    title: str
    description: str
    imdb_rating: float


class Film(FilmBase):
    genre: list[str]
    actors: Optional[list[Person]]
    writers: Optional[list[Person]]
    director: Optional[list[str]]


class Films(BaseModel):
    found: int
    pages: int
    per_page: int
    page:int
    data: list[FilmBase]
