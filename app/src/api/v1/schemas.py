from typing import Optional

import orjson
from pydantic import BaseModel

from src.models.models import orjson_dumps


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


class PersonSchema(UUIDBaseClass):
    name: str


class GenreSchema(UUIDBaseClass):
    name: str


class BaseFilmSchema(UUIDBaseClass):
    title: str
    description: str
    imdb_rating: float


class FilmSchema(BaseFilmSchema):
    genre: list[str]
    actors: Optional[list[PersonSchema]]
    writers: Optional[list[PersonSchema]]
    director: Optional[list[str]]


class FilmsSchema(BaseModel):
    meta: Pagination
    data: list[BaseFilmSchema]
