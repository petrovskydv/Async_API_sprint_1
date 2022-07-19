import math
from enum import Enum
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.paginator import Paginator
from src.api.v1.schemas import FilmsSchema, FilmSchema, Pagination
from src.services.film import FilmService, get_film_service

router = APIRouter()


@router.get('/{film_id}', response_model=FilmSchema, description='Информация о фильме')
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmSchema:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmSchema(**film.dict())


class SortDirection(Enum):
    asc = 'imdb_rating'
    desc = '-imdb_rating'


@router.get('/', response_model=FilmsSchema, description='Список фильмов')
async def get_films(
        film_service: FilmService = Depends(get_film_service),
        paginator: Paginator = Depends(),
        sort: SortDirection = Query(default=SortDirection.desc, description='Сортировка по рейтингу'),
        genre: Union[str, None] = Query(
            default=None, alias='filter[genre]', description='Поиск по жанру', example='comedy'
        ),
) -> FilmsSchema:
    films, found = await film_service.get_films(paginator.per_page, paginator.get_offset, sort.name, genre)
    total_pages = paginator.get_total_pages(found)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return FilmsSchema(
        meta=Pagination(found=found, page=paginator.page, pages=total_pages, per_page=paginator.per_page),
        data=films
    )


@router.get('/search', response_model=FilmsSchema, description='Поиск фильмов')
async def search_films(
        film_service: FilmService = Depends(get_film_service),
        per_page: int = Query(
            default=50, alias='page[size]', description='Количество элементов на странице', ge=1, le=500
        ),
        page: int = Query(default=1, alias='page[number]', description='Номер страницы', ge=1),
        query: Union[str, None] = Query(default=None, example='captain'),
) -> FilmsSchema:
    offset = (page - 1) * per_page
    films, found = [], 0
    total_pages = math.ceil(found / per_page)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return FilmsSchema(
        meta=Pagination(found=found, page=page, pages=total_pages, per_page=per_page),
        data=films
    )
