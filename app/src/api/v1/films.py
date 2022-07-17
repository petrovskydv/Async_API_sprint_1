from enum import Enum
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from src.models.film import Film
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return film


class SortDirection(Enum):
    asc = 'imdb_rating'
    desc = '-imdb_rating'


@router.get('/', response_model=list[Film], response_model_exclude={'actors', 'writers', 'genre', 'director'}, )
async def get_films(
        film_service: FilmService = Depends(get_film_service),
        per_page: int = 50,
        page: int = 0,
        sort: SortDirection = SortDirection.desc,
        genre: Union[str, None] = None
):
    offset = page * per_page
    films = await film_service.get_films(per_page, offset, sort.name, genre)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films
