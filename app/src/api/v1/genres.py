from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.paginator import Paginator
from src.api.v1.schemas import GenreSchema, GenresSchema, Pagination
from src.services.genre import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=GenreSchema, description='Информация о жанре')
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> GenreSchema:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return GenreSchema(**genre.dict())


@router.get('/', response_model=GenresSchema, description='Список жанров')
async def get_genres(
        genre_service: GenreService = Depends(get_genre_service),
        paginator: Paginator = Depends(),
) -> GenresSchema:
    genres, found = await genre_service.get_genres()
    total_pages = paginator.get_total_pages(found)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return GenresSchema(
        meta=Pagination(found=found, page=paginator.page, pages=total_pages, per_page=paginator.per_page),
        data=genres
    )
