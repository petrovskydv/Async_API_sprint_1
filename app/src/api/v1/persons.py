from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.schemas import PersonSchema, PersonsSchema, Pagination, BaseFilmSchema
from src.api.v1.paginator import Paginator
from src.services.person import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=PersonSchema, description='Информация о персоне')
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonSchema:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return PersonSchema(**person.dict())


@router.get('/search', response_model=PersonsSchema, description='Поиск по персонам')
async def get_persons(
        person_service: PersonService = Depends(get_person_service),
        paginator: Paginator = Depends(),
        query: Union[str, None] = Query(default=None, example='captain'),
) -> PersonsSchema:
    persons = []
    found = 0
    total_pages = paginator.get_total_pages(found)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonsSchema(
        meta=Pagination(found=found, page=paginator.page, pages=total_pages, per_page=paginator.per_page),
        data=persons
    )


@router.get('/{person_id}/films', response_model=list[BaseFilmSchema], description='Информация о персоне')
async def person_films(
        person_id: str, person_service: PersonService = Depends(get_person_service)
) -> list[BaseFilmSchema]:
    films = []
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return [BaseFilmSchema(**film.dict()) for film in films]
